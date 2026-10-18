// What happens when an application gets stuck, in order:
//   1. the AI navigator looks at the page and tries to finish the application itself;
//   2. a person is asked on the dashboard (and out loud on the Mac): in "auto" mode with a
//      time limit, after which the job is skipped and the run continues;
//   3. otherwise the job is marked "needs attention" and the run moves on.
// Things only a person may do (CAPTCHA, SMS codes, assessments, interviews) skip step 1.
// Email verification codes/links are read from her Gmail by the navigator (check_email);
// signing in / creating an account is done by the navigator with ATS_PASSWORD from .env.
import { navigate } from "./navigator.mjs";
import { ask, askForHelp, isSkip, loadProfile, log } from "./util.mjs";

// Only real person-only situations; a screening question that merely mentions "interview"
// or "test" in its label is still for the navigator.
const HUMAN_ONLY = /captcha|robot|two-factor|\bsms\b|\botp\b|skill assessment|coding (test|challenge)|(video|ai) interview/i;
// One navigator rescue per job per pass (keyed by job, since one tab is reused for every job).
const tried = new Map();

/** Step 1. Returns a result when the navigator finished (or decided to skip), else null. */
export async function tryNavigator(page, job, { reason, resumePath, mode }) {
  const id = `${job.platform}:${job.jobId}`;
  if (HUMAN_ONLY.test(reason) || Date.now() - (tried.get(id) ?? 0) < 10 * 60000) return null;
  tried.set(id, Date.now());
  log("info", `   stuck (${reason}) — letting the AI navigator try to finish it`);
  const r = await navigate(page, {
    rules: `- Stay on this job's page and its application dialog. Never use the site's search box, never open other jobs or pages.
- If the page says the job is closed / no longer accepting applications / expired, or there is no Apply button at all, use done with status "not_eligible".`,
    goal: `Finish and submit the job application for "${job.title}" at ${job.company} that is open on this page. The automatic filler got stuck here: ${reason}. Look at the screenshot, fix what's missing (fill empty or invalid fields, upload the resume, answer questions, tick required consent boxes), scroll to find more fields and the Next/Submit button, go through every remaining step and submit. Use done "applied" only when the site confirms the application.`,
    profile: loadProfile(),
    job,
    resumePath,
    mode: mode === "review" ? "review" : "auto",
  }).catch((e) => {
    if (isSkip(e)) throw e;
    return { status: "needs_attention", note: e.message };
  });
  if (r.status === "applied" || r.status === "skipped") return r;
  log("dim", `   navigator couldn't finish: ${r.note}`);
  return null;
}

/**
 * Step 2. Ask a person. Returns the chosen value ("" = continue, "done" = they submitted it,
 * "s" = skip) or null when nobody can be asked.
 */
export async function askPerson(page, question, choices, mode) {
  await page?.bringToFront?.().catch(() => {});
  if (mode === "auto") return askForHelp(question, choices);
  return ask(question, choices);
}
