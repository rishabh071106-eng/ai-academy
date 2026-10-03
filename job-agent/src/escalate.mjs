// What happens when an application gets stuck, in order:
//   1. the AI navigator looks at the page and tries to finish the application itself;
//   2. a person is asked on the dashboard (and out loud on the Mac): in "auto" mode with a
//      time limit, after which the job is skipped and the run continues;
//   3. otherwise the job is marked "needs attention" and the run moves on.
// Things only a person may do (CAPTCHA, email/phone verification, sign-in, assessments,
// interviews) skip step 1.
import { navigate } from "./navigator.mjs";
import { ask, askForHelp, loadProfile, log } from "./util.mjs";

const HUMAN_ONLY = /captcha|robot|verif|sign ?in|log ?in|password|two-factor|otp|assessment|interview|test\b|quiz/i;
const tried = new WeakSet();

/** Step 1. Returns a result when the navigator finished (or decided to skip), else null. */
export async function tryNavigator(page, job, { reason, resumePath, mode }) {
  if (HUMAN_ONLY.test(reason) || tried.has(page)) return null;
  tried.add(page);
  log("info", `   stuck (${reason}) — letting the AI navigator try to finish it`);
  const r = await navigate(page, {
    goal: `Finish and submit the job application that is open on this page, for "${job.title}" at ${job.company}. Fill anything still empty (use fill_form), upload the resume if asked (upload_resume), go through the remaining steps and submit. Use done "applied" when the site confirms the application.`,
    profile: loadProfile(),
    job,
    resumePath,
    mode: mode === "review" ? "review" : "auto",
    maxSteps: 20,
  }).catch((e) => ({ status: "needs_attention", note: e.message }));
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
