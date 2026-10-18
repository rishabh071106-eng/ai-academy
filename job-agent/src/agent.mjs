// The job agent: search → read job → score + tailor resume with Claude → apply → track.
//   npm run agent                         # review mode: you confirm every submit in the terminal
//   npm run agent -- --mode=auto          # submits on its own (still stops on questions it can't answer truthfully)
//   npm run agent -- --mode=dry-run       # find, score and tailor resumes only; apply later yourself
//   npm run agent -- --platform=naukri --max=5
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { connect, openAgentWindow } from "./browser.mjs";
import { applyExternal, applyLinkInText } from "./external.mjs";
import { syncProfile } from "./profile-sync.mjs";
import { evaluateAndTailor } from "./llm.mjs";
import * as linkedin from "./linkedin.mjs";
import * as naukri from "./naukri.mjs";
import * as alignerr from "./alignerr.mjs";
import { buildResumePdf, closePdfBrowser } from "./resume.mjs";
import * as tracker from "./tracker.mjs";
import { checkSkip, DATA_DIR, isSkip, jobControl, loadConfig, loadProfile, log, randomBetween, sleep } from "./util.mjs";

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
// Start each run by going back to jobs that were found earlier but not applied yet.
const retryUnfinished = args.retry !== undefined ? args.retry !== "false" : config.retryUnfinished !== false;
const UNFINISHED = new Set(["needs_attention", "external", "shortlisted"]);
const maxPages = Number(config.maxResultPagesPerSearch ?? 5);
const recheckMinutes = Number(config.recheckMinutes ?? 30);
const platforms = { linkedin, naukri, alignerr };
let currentRow = null; // { key, jobId, title, company } of the job being worked on
let attemptCounted = false; // applyTo bumped the job's attempt counter in this pass
let roundProgress = 0; // new jobs seen + applications made in the current round

// "Skip this job" from the dashboard.
process.on("message", (m) => {
  if (m?.type !== "skip") return;
  if (!jobControl.active || !currentRow) {
    log("dim", "  (skip asked, but no job is in progress right now)");
    return;
  }
  jobControl.skip = true;
  log("warn", `  ⏭ Skip requested for ${currentRow.title || "this job"} — stopping it…`);
});
const DONE = new Set(["applied", "interview", "offer", "rejected", "withdrawn", "skipped", "external", "needs_attention", "unable"]);

const todo = Object.values(profile.applicationAnswers ?? {}).filter((v) => typeof v === "string" && v.startsWith("TODO"));
if (todo.length) log("warn", `profile.json has ${todo.length} TODO answers (notice period, CTC…). Questions needing them will pause for you.`);
log("info", `Mode: ${mode} · apply to up to ${maxApply} · review ${reviewLimit || "all"} jobs${keepGoing ? " · keep going until done" : ""}`);

// One bad page or network hiccup must never end the run.
process.on("unhandledRejection", (e) => log("err", `  (recovered) ${String(e?.message ?? e).split("\n")[0]}`));
process.on("uncaughtException", (e) => log("err", `  (recovered) ${String(e?.message ?? e).split("\n")[0]}`));

// Jobs whose page showed LinkedIn's "unusual activity" warning were saved under that text as
// the title and skipped; put them back on the to-do list so they're tried again later.
// Jobs skipped while the rule was "Magento / PHP only" are forgotten so React roles get a fresh look.
for (const r of tracker.loadAll()) {
  if (/unusual activity on your account/i.test(r.title || "")) tracker.update(r.id, { title: "(LinkedIn job, not read yet)", company: "", status: "needs_attention", skipReason: null, historyNote: "LinkedIn showed a security check instead of the job; will retry" });
  else if (r.status === "skipped" && (r.history ?? []).some((h) => /^No magento \/ adobe commerce \/ php in the job post$/i.test(h.note || ""))) tracker.remove(r.id);
}

const MAX_ATTEMPTS = Number(config.maxAttemptsPerJob ?? 3);
// Per round: a few old jobs are retried, then every search runs — so new jobs get applied to
// every round instead of after all the old ones. The old ones rotate through over the rounds.
const RETRY_BATCH = Number(config.retryBatchSize ?? 5);
const MAX_MINUTES_PER_JOB = Number(config.maxMinutesPerJob ?? 6);
/** A job that used up its attempts without being applied is closed as "Couldn't apply" (status unable). */
function giveUpIfExhausted(key, jobId) {
  const row = tracker.find(key, jobId);
  if (!row || !UNFINISHED.has(row.status) || (row.attempts ?? 0) < MAX_ATTEMPTS) return false;
  const why = row.lastNote || row.history?.at(-1)?.note || "";
  tracker.upsert(key, jobId, { status: "unable", historyNote: `Couldn't apply after ${row.attempts} tries${why ? ` — ${why}` : ""}`, lastNote: why });
  log("warn", `  ✖ couldn't apply after ${row.attempts} tries — marked "Couldn't apply" on the dashboard`);
  return true;
}
// Old jobs that already used up their attempts are closed now, so the to-do list only holds jobs still worth trying.
for (const r of tracker.loadAll()) if (UNFINISHED.has(r.status) && (r.attempts ?? 0) >= MAX_ATTEMPTS) giveUpIfExhausted(r.platform, r.jobId);

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
  Object.assign(jobControl, { active: false, skip: false, deadline: 0 });
  // Put her own resume back on Naukri before going (the dashboard allows up to a minute).
  await Promise.race([restoreNaukriResume(), new Promise((r) => setTimeout(r, 45000))]).catch(() => {});
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
const isRelevantGlobal = (text) => !(config.relevantKeywords ?? []).length || relevantRe.test(text);
const reFor = (words) => new RegExp(`(^|[^a-z])(${words.map((k) => k.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})([^a-z]|$)`, "i");
let isRelevant = isRelevantGlobal;
// Keyword must be in the job's own title/description, not in sidebar text of the page.
// (When the description is the whole page text, only the title counts.)
const hitInTitleOrPost = (job, word) =>
  reFor([word]).test(job.title || "") || (String(job.description || "").length < (job.pageTextLength || Infinity) * 0.9 && reFor([word]).test(job.description));
const keywordHit = (job) => mustApply.find((k) => k.re.test(`${job.title}\n${job.description}`))?.word;
// Hard rule (config "requiredKeywords", e.g. Magento / Adobe Commerce / PHP): a job is only
// considered when its own title or description contains one of these words.
const requiredFor = (pcfg) => pcfg.requiredKeywords ?? config.requiredKeywords ?? [];
// (A cheap pre-filter; the AI check that follows still applies the location and fit rules.)
const requiredHit = (job, words) => !words.length || reFor(words).test(`${job.title}\n${job.description}`);
let applied = 0;
const stats = { scanned: 0, matched: 0, applied: 0, attention: 0, skipped: 0 };

try {
for (const [key, mod] of Object.entries(platforms)) {
  const pcfg = config.platforms[key];
  if (!pcfg?.enabled || (args.platform && args.platform !== key)) continue;
  // A platform can widen what counts as relevant (e.g. Alignerr's "AI trainer – coding" roles).
  isRelevant = pcfg.relevantKeywords?.length ? ((re) => (t) => re.test(t) || isRelevantGlobal(t))(reFor(pcfg.relevantKeywords)) : isRelevantGlobal;
  let page = await openAgentWindow(context, key);
  openPages.add(page);
  // Reopen the window / reconnect to Chrome if something closed it.
  const ensurePage = async () => {
    if (!context.browser()?.isConnected?.() && context.browser()) ({ context } = await connect());
    if (page.isClosed()) {
      page = await openAgentWindow(context, key);
      openPages.add(page);
      log("dim", "  (reopened the agent's window)");
    }
  };
  const done = () => applied >= maxApply || (reviewLimit > 0 && stats.scanned >= reviewLimit);
  const retriedThisRun = new Set();
  let moreRetries = false;
  try {
   for (let round = 1; ; round++) {
    roundProgress = 0;
    // Round 1 begins with the unfinished jobs from earlier runs.
    // Every round starts by finishing the jobs that are still open (best matches first),
    // before looking for new ones. A job gets at most MAX_ATTEMPTS tries.
    // Order: the keywords in requiredKeywords (Magento / Adobe Commerce first, then PHP, then
    // React…) looked up in the title and match reasons, then the better match first.
    const priorityWords = requiredFor(pcfg);
    const priority = (r) => {
      const text = `${r.title || ""}\n${(r.matchReasons || []).join(" ")}`;
      const i = priorityWords.findIndex((w) => reFor([w]).test(text));
      return i < 0 ? priorityWords.length : i;
    };
    const allRetries = retryUnfinished
      ? tracker.loadAll().filter((r) => r.platform === key && UNFINISHED.has(r.status) && r.url && !/^manual-/.test(r.jobId) && (r.attempts ?? 0) < MAX_ATTEMPTS).sort((a, b) => priority(a) - priority(b) || (b.matchScore ?? 0) - (a.matchScore ?? 0)).map((r) => ({ jobId: r.jobId, url: r.url, listUrl: r.listUrl, cardText: "", title: r.title }))
      : [];
    // Next batch of old jobs not yet retried in this run; once every one has had a turn, start over.
    let fresh = allRetries.filter((r) => !retriedThisRun.has(r.jobId));
    if (!fresh.length && allRetries.length) {
      retriedThisRun.clear();
      fresh = allRetries;
    }
    const retryList = fresh.slice(0, RETRY_BATCH);
    retryList.forEach((r) => retriedThisRun.add(r.jobId));
    moreRetries = fresh.length > retryList.length;
    // New postings first (so applications happen every round), then a batch of old jobs.
    for (const s of [...(pcfg.searches ?? []), ...(retryList.length ? [{ retry: true, keywords: "unfinished jobs", location: "from earlier runs" }] : [])]) {
     if (s.retry) log("info", `\n[${key}] Retrying ${retryList.length} of ${allRetries.length} old job(s) not applied yet…`);
     for (let pageIndex = 0; pageIndex < maxPages; pageIndex++) {
      if (done()) break;
      await ensurePage().catch(() => {});
      if (s.retry && pageIndex > 0) break;
      if (!s.retry) log("info", `\n[${key}] Searching "${s.keywords}" in ${s.location}${pageIndex ? ` (results page ${pageIndex + 1})` : ""}…`);
      let refs = [];
      if (s.retry) {
        if (pageIndex > 0) break;
        refs = retryList;
      } else try {
        refs = await mod.search(page, s, { ...pcfg, max: config.maxJobsToScanPerSearch, pageIndex });
      } catch (e) {
        log("err", `  search failed: ${e.message.split("\n")[0]}`);
        break;
      }
      if (!refs.length) break;
      const unseen = refs.filter((r) => !tracker.find(key, r.jobId)).length;
      roundProgress += unseen;
      // Cheap relevance check on the result cards, before opening anything (not for retries:
      // those were already read, and the keyword may only be in the description).
      const offTopic = s.retry ? [] : refs.filter((r) => r.cardText && !isRelevant(r.cardText));
      refs = refs.filter((r) => !offTopic.includes(r));
      log("dim", `  ${refs.length + offTopic.length} jobs found, ${refs.length} look relevant`);
      if (offTopic.length) log("dim", `  ignoring off-topic: ${offTopic.slice(0, 6).map((r) => r.cardText.split(/ · |\n/)[0].slice(0, 45)).join(" | ")}${offTopic.length > 6 ? " …" : ""}`);

      for (const ref of refs) {
        if (done()) break;
       try {
        await ensurePage();
        const existing = tracker.find(key, ref.jobId);
        // A job already handled (applied, skipped, waiting for a person…) is only revisited
        // through the retry list at the start of a round.
        if (existing && !s.retry && (DONE.has(existing.status) || mode === "dry-run")) continue;
        stats.scanned++;
        attemptCounted = false;
        Object.assign(jobControl, { active: true, skip: false, deadline: MAX_MINUTES_PER_JOB > 0 ? Date.now() + MAX_MINUTES_PER_JOB * 60000 : 0 });
        currentRow = { key, jobId: ref.jobId, title: ref.title || existing?.title || "", company: existing?.company || "" };

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
        const required = requiredFor(pcfg);
        if (!requiredHit(job, required)) {
          log("dim", `• ${job.title || job.url} — no ${required.join(" / ")} in the job post, skipping`);
          tracker.upsert(key, job.jobId, { url: job.url, title: job.title, company: job.company, location: job.location, status: "skipped", skipReason: "offtopic", historyNote: `No ${required.join(" / ")} in the job post` });
          stats.skipped++;
          continue;
        }
        if (!isRelevant(`${job.title}\n${job.description}`)) {
          log("dim", `• ${job.title || job.url} — not a Magento/PHP/React/front-end/full-stack role, skipping`);
          tracker.upsert(key, job.jobId, { url: job.url, title: job.title, company: job.company, location: job.location, status: "skipped", skipReason: "offtopic", historyNote: "Off-topic (none of her core skills mentioned)" });
          stats.skipped++;
          continue;
        }
        if (/build your professional brand|join linkedin|sign in to (view|see)|feed post|linkedin feed/i.test(`${job.title} ${job.company}`)) {
          log("dim", `  not a job page (${job.title || job.url}) — skipping`);
          continue;
        }
        const base = { url: job.url, title: job.title, company: job.company, location: job.location, ...(ref.listUrl ? { listUrl: ref.listUrl } : {}) };
        currentRow = { key, jobId: job.jobId, title: job.title, company: job.company };
        process.send?.({ type: "job", title: job.title, company: job.company, url: job.url });
        log("info", `• ${job.title || "(reading job…)"} — ${job.company || ""}`);
        log("dim", `  read ${job.description.length.toLocaleString()} characters${job.expanded ? ` (opened ${job.expanded} "see more")` : ""}`);

        if (job.closed) {
          tracker.upsert(key, job.jobId, { ...base, status: "skipped", skipReason: "closed", historyNote: "The job is closed / no longer accepting applications" });
          log("dim", "  closed — no longer accepting applications");
          stats.skipped++;
          continue;
        }
        if (job.alreadyApplied) {
          tracker.upsert(key, job.jobId, { ...base, status: "applied", historyNote: "Already applied before the agent saw it" });
          log("dim", "  already applied");
          continue;
        }
        // Whole words only: "intern" must not exclude "International".
        const excludedTitle = (config.excludeTitleKeywords ?? []).find((k) => reFor([k]).test(job.title || ""));
        const excludedCompany = (config.excludeCompanies ?? []).find((c) => (job.company || "").toLowerCase().includes(c.toLowerCase()));
        if (excludedTitle || excludedCompany) {
          tracker.upsert(key, job.jobId, { ...base, status: "skipped", skipReason: "excluded", historyNote: `Excluded by config (${excludedTitle || excludedCompany})` });
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
          log("err", `  AI evaluation failed: ${e.message}`);
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
        // The keyword override only rescues borderline scores; it must not push through
        // off-target jobs (other countries, Java-only, non-job pages) that score low.
        if ((!ev.shouldApply || ev.matchScore < config.minMatchScore) && hit && ev.matchScore >= Number(config.keywordOverrideMinScore ?? 45) && hitInTitleOrPost(job, hit)) {
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
        currentRow = { key, jobId: job.jobId, title: job.title, company: job.company };
        process.send?.({ type: "job", title: job.title, company: job.company, url: job.url, matchScore: ev.matchScore });
        checkSkip();

        if (job.applyType === "none") {
          // No Apply control on the page: closed, already applied, or it didn't render. Tried again later (bounded by attempts).
          tracker.upsert(key, job.jobId, { ...scored, resumeFile, status: "needs_attention", historyNote: "No Apply button on the job page (closed, already applied, or it didn't load)", lastNote: "No Apply button on the job page" });
          log("warn", "  no Apply button on the page — will look again later");
          stats.attention++;
          continue;
        }
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
        if (isSkip(e) || jobControl.skip) {
          // Skipped by you from the dashboard, or over the time limit. Never overwrite a finished application.
          const row = currentRow && tracker.find(key, currentRow.jobId);
          const timedOut = e?.timeout && !jobControl.skip;
          const ids = { url: ref.url, ...(currentRow?.title ? { title: currentRow.title } : {}), ...(currentRow?.company ? { company: currentRow.company } : {}) };
          if (!row || !["applied", "interview", "offer"].includes(row.status))
            try {
              if (timedOut) {
                const note = `Took too long (over ${MAX_MINUTES_PER_JOB} min) — will try again later`;
                tracker.upsert(key, currentRow?.jobId ?? ref.jobId, { ...ids, status: "needs_attention", historyNote: note, lastNote: note, attempts: (row?.attempts ?? 0) + 1 });
                attemptCounted = true;
                giveUpIfExhausted(key, currentRow?.jobId ?? ref.jobId);
              } else tracker.upsert(key, currentRow?.jobId ?? ref.jobId, { ...ids, status: "skipped", skipReason: "user", historyNote: "Skipped by you", lastNote: "Skipped by you" });
            } catch (e2) {
              log("warn", `  couldn't record the skip: ${e2.message}`);
            }
          if (timedOut) {
            stats.attention++;
            log("warn", `  ⏱ over ${MAX_MINUTES_PER_JOB} min on this job — moving on (it gets another try later)`);
          } else {
            stats.skipped++;
            log("warn", "  ⏭ skipped by you — on to the next job");
          }
          await page.keyboard.press("Escape").catch(() => {});
        } else {
          // Anything unexpected on one job: note it and move on to the next.
          log("err", `  error on ${ref.url}: ${String(e?.message ?? e).split("\n")[0]} — moving on`);
        }
       } finally {
        // A retried job that got nowhere this pass still used up one of its attempts.
        if (s.retry && !attemptCounted) {
          try {
            const row = tracker.find(key, ref.jobId);
            if (row && UNFINISHED.has(row.status)) {
              tracker.upsert(key, ref.jobId, { attempts: (row.attempts ?? 0) + 1 });
              giveUpIfExhausted(key, ref.jobId);
            }
          } catch {}
        }
        Object.assign(jobControl, { active: false, skip: false, deadline: 0 });
        currentRow = null;
        process.send?.({ type: "job", title: null });
       }
      }
      // Deeper result pages only help while they still contain jobs we haven't seen.
      if (pageIndex > 0 && !unseen) break;
     }
    }
    if (done() || !keepGoing) break;
    if (roundProgress === 0 && !moreRetries) {
      // Nothing new and nothing applied this round: wait before looking again (retries included).
      log("info", `\n[${key}] Every current job has been reviewed (${applied}/${maxApply} applied). Checking for new postings in ${recheckMinutes} min — press Stop to end.`);
      await sleep(recheckMinutes * 60000);
    }
   }
  } finally {
    // Keep the tab: closing the last tab of a window closes the window in her Chrome.
  }
}
} catch (e) {
  // An error outside a single job (search set-up, tracker lock…): stop so the dashboard restarts the agent.
  log("err", `■ Unexpected error: ${String(e?.message ?? e).split("\n")[0]} — restarting`);
  await restoreNaukriResume();
  await closePdfBrowser().catch(() => {});
  process.exit(1);
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
    if (isSkip(e)) throw e;
    result = { status: "needs_attention", note: `Error: ${e.message}` };
  }
  // A skip asked while the form was being filled wins over whatever the form step reported
  // (unless it got submitted in the meantime).
  if (jobControl.skip && result.status !== "applied") checkSkip();
  const attempts = (tracker.find(key, job.jobId)?.attempts ?? 0) + (result.status === "applied" ? 0 : 1);
  attemptCounted = true;
  tracker.upsert(key, job.jobId, { status: result.status, historyNote: result.note, lastNote: result.note, attempts });
  if (result.status !== "applied") giveUpIfExhausted(key, job.jobId);
  if (result.status === "applied") {
    jobControl.deadline = 0;
    await maybeMessage(mod, key, page, job);
    applied++;
    stats.applied++;
    roundProgress++;
    log("ok", `  ✔ applied (${applied}/${maxApply})`);
    jobControl.active = false; // nothing left to skip during the pause between applications
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
    // A sent message is noted on the job; it never counts as an application.
    tracker.upsert(key, job.jobId, { messageStatus: r.status, messageNote: r.note, ...(r.status === "sent" ? { historyNote: r.note } : {}) });
    log(r.status === "sent" ? "ok" : "dim", `  ✉ ${r.note}`);
  } catch (e) {
    tracker.upsert(key, job.jobId, { messageStatus: "draft", messageNote: `Couldn't send: ${e.message}` });
  }
}

// Put her normal resume back on Naukri after a run that uploaded tailored ones
// (also on Stop from the dashboard, see shutdown()).
let restored = false;
async function restoreNaukriResume() {
  if (restored || !naukri.apply.uploaded || config.platforms.naukri?.restoreBaseResumeAfterRun === false) return;
  restored = true;
  try {
    const custom = (config.platforms.naukri.baseResumePath || "").replace(/^~(?=\/)/, os.homedir());
    const base = custom && fs.existsSync(custom) ? custom : baseResume?.path ?? (await buildResumePdf(profile, {}, { platform: "base", jobId: "profile", company: "base" }));
    log("info", "\nRestoring your normal resume on Naukri…");
    const tab = [...openPages].filter((p) => !p.isClosed()).at(-1) ?? (await context.newPage());
    const ok = await naukri.uploadResume(tab, base);
    log(ok ? "ok" : "warn", ok ? `  ${path.basename(base)} is back on your Naukri profile` : "  couldn't confirm; check your Naukri profile resume");
  } catch (e) {
    log("warn", `  couldn't restore the base resume: ${e.message}`);
  }
}
await restoreNaukriResume();

await closePdfBrowser();
log("ok", `\nDone. Scanned ${stats.scanned} · matched ${stats.matched} · applied ${stats.applied} · needs attention ${stats.attention} · skipped ${stats.skipped}`);
log("info", "Open the dashboard: npm run dashboard");
process.exit(0);
