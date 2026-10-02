// The job agent: search → read job → score + tailor resume with Claude → apply → track.
//   npm run agent                         # review mode: you confirm every submit in the terminal
//   npm run agent -- --mode=auto          # submits on its own (still stops on questions it can't answer truthfully)
//   npm run agent -- --mode=dry-run       # find, score and tailor resumes only; apply later yourself
//   npm run agent -- --platform=naukri --max=5
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { connect } from "./browser.mjs";
import { applyExternal, applyLinkInText } from "./external.mjs";
import { syncProfile } from "./profile-sync.mjs";
import { evaluateAndTailor } from "./llm.mjs";
import * as linkedin from "./linkedin.mjs";
import * as naukri from "./naukri.mjs";
import { buildResumePdf, closePdfBrowser } from "./resume.mjs";
import * as tracker from "./tracker.mjs";
import { DATA_DIR, loadConfig, loadProfile, log, randomBetween, sleep } from "./util.mjs";

const args = Object.fromEntries(process.argv.slice(2).map((a) => a.replace(/^--/, "").split("=")));
const config = loadConfig();
// Step 0: make sure we work from her latest resume (re-reads it if Downloads has a newer one).
const baseResume = await syncProfile(config);
const profile = loadProfile();
const mode = args.mode ?? config.mode ?? "review";
const maxApply = Number(args.max ?? config.maxApplicationsPerRun ?? 15);
// 0 = no limit: review every job the searches return (across result pages).
const reviewLimit = Number(args.review ?? config.maxJobsToReview ?? 0);
const keepGoing = args["keep-going"] !== undefined ? args["keep-going"] !== "false" : !!config.keepGoing;
const maxPages = Number(config.maxResultPagesPerSearch ?? 5);
const recheckMinutes = Number(config.recheckMinutes ?? 30);
const platforms = { linkedin, naukri };
const DONE = new Set(["applied", "interview", "offer", "rejected", "withdrawn", "skipped", "external", "needs_attention"]);

const todo = Object.values(profile.applicationAnswers ?? {}).filter((v) => typeof v === "string" && v.startsWith("TODO"));
if (todo.length) log("warn", `profile.json has ${todo.length} TODO answers (notice period, CTC…). Questions needing them will pause for you.`);
log("info", `Mode: ${mode} · apply to up to ${maxApply} · review ${reviewLimit || "all"} jobs${keepGoing ? " · keep going until done" : ""}`);

// One bad page or network hiccup must never end the run.
process.on("unhandledRejection", (e) => log("err", `  (recovered) ${String(e?.message ?? e).split("\n")[0]}`));
process.on("uncaughtException", (e) => log("err", `  (recovered) ${String(e?.message ?? e).split("\n")[0]}`));

let context;
try {
  ({ context } = await connect());
} catch (e) {
  log("err", e.message);
  process.exit(1);
}
const openPages = new Set();
const shutdown = async () => {
  log("warn", "Stopping agent…");
  // Leave the agent's tab open in Chrome; never close the user's browser.
  await closePdfBrowser().catch(() => {});
  process.exit(0);
};
process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);

// Jobs mentioning any of these are applied to even when Claude's score is low.
const mustApply = (config.alwaysApplyKeywords ?? []).map((k) => ({
  word: k,
  re: new RegExp(`(^|[^a-z])${k.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}([^a-z]|$)`, "i"),
}));
// A job is worth reading only if it mentions at least one of her core areas.
const relevantRe = new RegExp(`(^|[^a-z])(${(config.relevantKeywords ?? []).map((k) => k.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})([^a-z]|$)`, "i");
const isRelevant = (text) => !(config.relevantKeywords ?? []).length || relevantRe.test(text);
const keywordHit = (job) => mustApply.find((k) => k.re.test(`${job.title}\n${job.description}`))?.word;
let applied = 0;
const stats = { scanned: 0, matched: 0, applied: 0, attention: 0, skipped: 0 };

for (const [key, mod] of Object.entries(platforms)) {
  const pcfg = config.platforms[key];
  if (!pcfg?.enabled || (args.platform && args.platform !== key)) continue;
  let page = await context.newPage();
  openPages.add(page);
  // Reopen the tab / reconnect to Chrome if something closed it.
  const ensurePage = async () => {
    if (!context.browser()?.isConnected?.() && context.browser()) ({ context } = await connect());
    if (page.isClosed()) {
      page = await context.newPage();
      openPages.add(page);
      log("dim", "  (reopened the agent's tab)");
    }
  };
  const done = () => applied >= maxApply || (reviewLimit > 0 && stats.scanned >= reviewLimit);
  try {
   for (let round = 1; ; round++) {
    const reviewedBefore = stats.scanned;
    for (const s of pcfg.searches) {
     for (let pageIndex = 0; pageIndex < maxPages; pageIndex++) {
      if (done()) break;
      await ensurePage().catch(() => {});
      log("info", `\n[${key}] Searching "${s.keywords}" in ${s.location}${pageIndex ? ` (results page ${pageIndex + 1})` : ""}…`);
      let refs = [];
      try {
        refs = await mod.search(page, s, { ...pcfg, max: config.maxJobsToScanPerSearch, pageIndex });
      } catch (e) {
        log("err", `  search failed: ${e.message.split("\n")[0]}`);
        break;
      }
      if (!refs.length) break;
      const unseen = refs.filter((r) => !tracker.find(key, r.jobId)).length;
      // Cheap relevance check on the result cards, before opening anything.
      const offTopic = refs.filter((r) => r.cardText && !isRelevant(r.cardText));
      refs = refs.filter((r) => !offTopic.includes(r));
      log("dim", `  ${refs.length + offTopic.length} jobs found, ${refs.length} look relevant`);
      if (offTopic.length) log("dim", `  ignoring off-topic: ${offTopic.slice(0, 6).map((r) => r.cardText.split(/ · |\n/)[0].slice(0, 45)).join(" | ")}${offTopic.length > 6 ? " …" : ""}`);

      for (const ref of refs) {
        if (done()) break;
       try {
        await ensurePage();
        const existing = tracker.find(key, ref.jobId);
        // Low-score skips get a second look (matching rules may have changed); exclusions don't.
        const retry = existing?.status === "skipped" && !["excluded", "offtopic"].includes(existing.skipReason);
        if (existing && !retry && (DONE.has(existing.status) || mode === "dry-run")) continue;
        stats.scanned++;

        let job;
        try {
          job = { platform: key, ...(await mod.getJob(page, ref)) };
        } catch (e) {
          log("err", `  could not read ${ref.url}: ${e.message.split("\n")[0]}`);
          continue;
        }
        if ((job.description ?? "").length < 200) {
          // The page didn't render (logged out, captcha, slow network). Save what we saw and move on.
          const shot = path.join(DATA_DIR, "debug", `${key}-${job.jobId}.png`);
          fs.mkdirSync(path.dirname(shot), { recursive: true });
          await page.screenshot({ path: shot }).catch(() => {});
          log("err", `  couldn't read the job page (${ref.url}) — screenshot saved to data/debug/`);
          continue;
        }
        if (!isRelevant(`${job.title}\n${job.description}`)) {
          log("dim", `• ${job.title || job.url} — not a Magento/PHP/React/front-end/full-stack role, skipping`);
          tracker.upsert(key, job.jobId, { url: job.url, title: job.title, company: job.company, location: job.location, status: "skipped", skipReason: "offtopic", historyNote: "Off-topic (none of her core skills mentioned)" });
          stats.skipped++;
          continue;
        }
        const base = { url: job.url, title: job.title, company: job.company, location: job.location };
        log("info", `• ${job.title || "(reading job…)"} — ${job.company || ""}`);
        log("dim", `  read ${job.description.length.toLocaleString()} characters${job.expanded ? ` (opened ${job.expanded} "see more")` : ""}`);

        if (job.alreadyApplied) {
          tracker.upsert(key, job.jobId, { ...base, status: "applied", historyNote: "Already applied before the agent saw it" });
          log("dim", "  already applied");
          continue;
        }
        const lower = `${job.title}`.toLowerCase();
        if (config.excludeTitleKeywords.some((k) => lower.includes(k)) || config.excludeCompanies.some((c) => job.company.toLowerCase().includes(c.toLowerCase()))) {
          tracker.upsert(key, job.jobId, { ...base, status: "skipped", skipReason: "excluded", historyNote: "Excluded by config" });
          stats.skipped++;
          continue;
        }

        // A dry run already scored this job and tailored a resume: reuse them.
        if (existing?.status === "shortlisted" && existing.resumeFile && fs.existsSync(path.join(DATA_DIR, existing.resumeFile)) && job.applyType === "easy" && mode !== "dry-run") {
          stats.matched++;
          await applyTo(mod, key, page, job, path.join(DATA_DIR, existing.resumeFile));
          continue;
        }

        log("dim", "  checking the job against her resume…");
        let ev;
        try {
          ev = await evaluateAndTailor(profile, job);
          if (!ev.descriptionComplete) {
            // Claude thinks the description was cut off: open the job again and re-read it once.
            log("dim", "  description looks cut off — opening the full job again");
            const again = { platform: key, ...(await mod.getJob(page, ref)) };
            if ((again.description ?? "").length > (job.description ?? "").length + 50) {
              Object.assign(job, { ...again, title: job.title || again.title, company: job.company || again.company });
              ev = await evaluateAndTailor(profile, job);
            }
          }
        } catch (e) {
          log("err", `  Claude evaluation failed: ${e.message}`);
          continue;
        }
        // Fill in anything the page selectors missed from what Claude read on the page.
        const wasMissing = !job.title || !job.company;
        job.title ||= ev.jobTitle;
        job.company ||= ev.company;
        job.location ||= ev.location;
        Object.assign(base, { title: job.title, company: job.company, location: job.location });
        if (wasMissing) log("dim", `  = ${job.title} — ${job.company}`);
        const scored = {
          ...base, matchScore: ev.matchScore, matchReasons: ev.matchReasons, missingSkills: ev.missingSkills,
          hiringContact: job.hiringContact ?? null, hiringMessage: ev.hiringMessage, messageStatus: "draft",
        };
        const hit = keywordHit(job);
        if ((!ev.shouldApply || ev.matchScore < config.minMatchScore) && hit) {
          scored.matchReasons = [`Mentions ${hit}, which is in her core stack`, ...scored.matchReasons];
          log("dim", `  score ${ev.matchScore}% but mentions "${hit}" — applying anyway`);
        } else if (!ev.shouldApply || ev.matchScore < config.minMatchScore) {
          tracker.upsert(key, job.jobId, { ...scored, status: "skipped", skipReason: "score", historyNote: `Match ${ev.matchScore}% — not her stack` });
          log("dim", `  match ${ev.matchScore}% — skipping: ${ev.missingSkills.slice(0, 3).join(", ") || ev.matchReasons[0] || "not her stack"}`);
          stats.skipped++;
          continue;
        }
        stats.matched++;
        const resumePath = await buildResumePdf(profile, ev.tailored, job);
        const resumeFile = path.relative(DATA_DIR, resumePath).split(path.sep).join("/");
        log("ok", `  match ${ev.matchScore}% — resume created for this job: data/${resumeFile}`);

        if (job.applyType !== "easy") {
          tracker.upsert(key, job.jobId, { ...scored, resumeFile, status: "external", historyNote: "Applies on the company's site" });
          const formLink = applyLinkInText(job.description);
          const coverLetter = ev.hiringMessage?.full?.replace(/^Hi[^,\n]*,/, "Dear Hiring Team,");
          if (mode !== "dry-run" && formLink && config.externalApply?.enabled !== false) {
            // The post says "apply via this Google Form".
            log("dim", `  application form in the post: ${formLink}`);
            const open = async (p) => {
              const tab = await p.context().newPage();
              await tab.goto(formLink, { waitUntil: "domcontentloaded" });
              return tab;
            };
            await applyTo(mod, key, page, job, resumePath, { external: true, open, coverLetter });
          } else if (mode !== "dry-run" && job.applyType === "external" && config.externalApply?.enabled !== false && mod.openCompanySite) {
            await applyTo(mod, key, page, job, resumePath, { external: true, coverLetter });
          } else if (mode !== "dry-run") {
            await maybeMessage(mod, key, page, job);
          }
          continue;
        }
        if (mode === "dry-run") {
          tracker.upsert(key, job.jobId, { ...scored, resumeFile, status: "shortlisted", historyNote: "Dry run" });
          continue;
        }
        tracker.upsert(key, job.jobId, { ...scored, resumeFile, status: "shortlisted" });
        await applyTo(mod, key, page, job, resumePath);
       } catch (e) {
        // Anything unexpected on one job: note it and move on to the next.
        log("err", `  error on ${ref.url}: ${String(e?.message ?? e).split("\n")[0]} — moving on`);
       }
      }
      // Deeper result pages only help while they still contain jobs we haven't seen.
      if (pageIndex > 0 && !unseen) break;
     }
    }
    if (done() || !keepGoing) break;
    if (stats.scanned === reviewedBefore) {
      log("info", `\n[${key}] Every current job has been reviewed (${applied}/${maxApply} applied). Checking for new postings in ${recheckMinutes} min — press Stop to end.`);
      await sleep(recheckMinutes * 60000);
    }
   }
  } finally {
    // Keep the tab: closing the last tab of a window closes the window in her Chrome.
  }
}

async function applyTo(mod, key, page, job, resumePath, { external = false, coverLetter, open } = {}) {
  let result;
  try {
    if (external) {
      log("info", "  applying on the company's site…");
      result = await applyExternal(page, job, { open: open ?? mod.openCompanySite, resumePath, profile, mode, coverLetter });
      // Back to the job page for the hiring-team message.
      if (!page.url().includes(new URL(job.url).hostname)) await page.goto(job.url, { waitUntil: "domcontentloaded" }).catch(() => {});
    } else {
      result = await mod.apply(page, job, { resumePath, profile, mode, cfg: config.platforms[key] ?? {} });
    }
  } catch (e) {
    result = { status: "needs_attention", note: `Error: ${e.message}` };
  }
  tracker.upsert(key, job.jobId, { status: result.status, historyNote: result.note, lastNote: result.note });
  if (result.status === "applied") {
    await maybeMessage(mod, key, page, job);
    applied++;
    stats.applied++;
    log("ok", `  ✔ applied (${applied}/${maxApply})`);
    const [lo, hi] = config.delaySecondsBetweenApplications;
    await sleep(randomBetween(lo, hi) * 1000);
  } else {
    if (result.status === "needs_attention") stats.attention++;
    log("warn", `  ${result.status}: ${result.note}`);
  }
}

async function maybeMessage(mod, key, page, job) {
  const row = tracker.find(key, job.jobId);
  if (!config.hiringMessage?.enabled || !mod.messageHiringTeam || !row?.hiringMessage || !job.hiringContact) return;
  try {
    const r = await mod.messageHiringTeam(page, job, row.hiringMessage, { mode, autoSend: config.hiringMessage.autoSend });
    tracker.upsert(key, job.jobId, { messageStatus: r.status, messageNote: r.note, ...(r.status === "sent" ? { historyNote: r.note, status: "applied" } : {}) });
    log(r.status === "sent" ? "ok" : "dim", `  ✉ ${r.note}`);
  } catch (e) {
    tracker.upsert(key, job.jobId, { messageStatus: "draft", messageNote: `Couldn't send: ${e.message}` });
  }
}

// Put her normal resume back on Naukri after a run that uploaded tailored ones.
if (naukri.apply.uploaded && config.platforms.naukri?.restoreBaseResumeAfterRun !== false) {
  try {
    const custom = (config.platforms.naukri.baseResumePath || "").replace(/^~(?=\/)/, os.homedir());
    const base = custom && fs.existsSync(custom) ? custom : baseResume?.path ?? (await buildResumePdf(profile, {}, { platform: "base", jobId: "profile", company: "base" }));
    log("info", "\nRestoring your normal resume on Naukri…");
    const tab = [...openPages].at(-1) ?? (await context.newPage());
    const ok = await naukri.uploadResume(tab, base);
    log(ok ? "ok" : "warn", ok ? `  ${path.basename(base)} is back on your Naukri profile` : "  couldn't confirm; check your Naukri profile resume");
  } catch (e) {
    log("warn", `  couldn't restore the base resume: ${e.message}`);
  }
}

await closePdfBrowser();
log("ok", `\nDone. Scanned ${stats.scanned} · matched ${stats.matched} · applied ${stats.applied} · needs attention ${stats.attention} · skipped ${stats.skipped}`);
log("info", "Open the dashboard: npm run dashboard");
process.exit(0);
