// The job agent: search → read job → score + tailor resume with Claude → apply → track.
//   npm run agent                         # review mode: you confirm every submit in the terminal
//   npm run agent -- --mode=auto          # submits on its own (still stops on questions it can't answer truthfully)
//   npm run agent -- --mode=dry-run       # find, score and tailor resumes only; apply later yourself
//   npm run agent -- --platform=naukri --max=5
import fs from "node:fs";
import path from "node:path";
import { connect } from "./browser.mjs";
import { evaluateAndTailor } from "./llm.mjs";
import * as linkedin from "./linkedin.mjs";
import * as naukri from "./naukri.mjs";
import { buildResumePdf, closePdfBrowser } from "./resume.mjs";
import * as tracker from "./tracker.mjs";
import { DATA_DIR, loadConfig, loadProfile, log, randomBetween, sleep } from "./util.mjs";

const args = Object.fromEntries(process.argv.slice(2).map((a) => a.replace(/^--/, "").split("=")));
const config = loadConfig();
const profile = loadProfile();
const mode = args.mode ?? config.mode ?? "review";
const maxApply = Number(args.max ?? config.maxApplicationsPerRun ?? 15);
const platforms = { linkedin, naukri };
const DONE = new Set(["applied", "interview", "offer", "rejected", "withdrawn", "skipped", "external", "needs_attention"]);

const todo = Object.values(profile.applicationAnswers ?? {}).filter((v) => typeof v === "string" && v.startsWith("TODO"));
if (todo.length) log("warn", `profile.json has ${todo.length} TODO answers (notice period, CTC…). Questions needing them will pause for you.`);
log("info", `Mode: ${mode} · max applications this run: ${maxApply}`);

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
  for (const p of openPages) await p.close().catch(() => {});
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
const keywordHit = (job) => mustApply.find((k) => k.re.test(`${job.title}\n${job.description}`))?.word;
let applied = 0;
const stats = { scanned: 0, matched: 0, applied: 0, attention: 0, skipped: 0 };

for (const [key, mod] of Object.entries(platforms)) {
  const pcfg = config.platforms[key];
  if (!pcfg?.enabled || (args.platform && args.platform !== key)) continue;
  const page = await context.newPage();
  openPages.add(page);
  try {
    for (const s of pcfg.searches) {
      if (applied >= maxApply) break;
      log("info", `\n[${key}] Searching "${s.keywords}" in ${s.location}…`);
      let refs = [];
      try {
        refs = await mod.search(page, s, { ...pcfg, max: config.maxJobsToScanPerSearch });
      } catch (e) {
        log("err", `  search failed: ${e.message.split("\n")[0]}`);
        continue;
      }
      log("dim", `  ${refs.length} jobs found`);

      for (const ref of refs) {
        if (applied >= maxApply) break;
        const existing = tracker.find(key, ref.jobId);
        // Low-score skips get a second look (matching rules may have changed); exclusions don't.
        const retry = existing?.status === "skipped" && existing.skipReason !== "excluded";
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
        log("ok", `  match ${ev.matchScore}% — tailored resume: data/${resumeFile}`);

        if (job.applyType !== "easy") {
          tracker.upsert(key, job.jobId, { ...scored, resumeFile, status: "external", historyNote: "Applies on company site — apply manually with the tailored resume" });
          continue;
        }
        if (mode === "dry-run") {
          tracker.upsert(key, job.jobId, { ...scored, resumeFile, status: "shortlisted", historyNote: "Dry run" });
          continue;
        }
        tracker.upsert(key, job.jobId, { ...scored, resumeFile, status: "shortlisted" });
        await applyTo(mod, key, page, job, resumePath);
      }
    }
  } finally {
    await page.close().catch(() => {});
  }
}

async function applyTo(mod, key, page, job, resumePath) {
  let result;
  try {
    result = await mod.apply(page, job, { resumePath, profile, mode });
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

await closePdfBrowser();
log("ok", `\nDone. Scanned ${stats.scanned} · matched ${stats.matched} · applied ${stats.applied} · needs attention ${stats.attention} · skipped ${stats.skipped}`);
log("info", "Open the dashboard: npm run dashboard");
process.exit(0);
