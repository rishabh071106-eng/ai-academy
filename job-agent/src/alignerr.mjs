// Alignerr (app.alignerr.com): AI-training / expert roles. Alignerr's app layout isn't a
// classic job board, so the agent uses the navigator (snapshot → Claude picks the next click →
// act) to find the list of roles and to go through each application. Skill assessments and
// AI interviews are hers to take: the navigator hands those over instead of doing them.
import { expandJob, readPage } from "./browser.mjs";
import { navigate } from "./navigator.mjs";
import { log, loadProfile, sleep, slugify } from "./util.mjs";

export const name = "alignerr";
const HOME = "https://app.alignerr.com/home";

async function loggedIn(page) {
  if (/\/(login|signin|sign-in|auth|sso)\b/i.test(page.url()) || /accounts\.google\.com/.test(page.url())) return false;
  const loginBtn = await page.getByRole("button", { name: /^(log ?in|sign ?in|continue with google|sign in with google)$/i }).filter({ visible: true }).count().catch(() => 0);
  return !loginBtn;
}

export async function search(page, s, cfg) {
  if (cfg.pageIndex) return []; // Alignerr shows one list
  await page.goto(cfg.url || HOME, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
  await sleep(2500);
  if (!(await loggedIn(page))) throw new Error("Alignerr is not logged in in this Chrome window — log in once at app.alignerr.com");

  const r = await navigate(page, {
    goal:
      "Find the list of open roles / projects / opportunities she can apply to on Alignerr (look in the home page, and tabs or menus like Opportunities, Jobs, Projects, Explore, Browse). " +
      "When the list is visible (scroll to load all of it), call report_jobs with EVERY role: its title, the element id that opens it or its Apply button, its href if it is a link, a one-line summary, and already_applied if it says applied/in review/started.",
    profile: loadProfile(),
    mode: "auto",
    maxSteps: 10,
    stopOnReport: true,
  });
  const listUrl = page.url();
  const jobs = (r.jobs || []).filter((j) => j.title);
  log("dim", `  Alignerr shows ${jobs.length} roles`);
  const kw = (s.keywords || "").toLowerCase().split(/\s+/).filter(Boolean);
  return jobs
    .filter((j) => !kw.length || kw.some((k) => `${j.title} ${j.summary}`.toLowerCase().includes(k)))
    .slice(0, cfg.max || 60)
    .map((j) => ({
      jobId: slugify(j.title),
      url: j.href ? new URL(j.href, listUrl).href : listUrl,
      listUrl,
      title: j.title,
      cardText: `${j.title} · ${j.summary || ""}`,
      alreadyApplied: !!j.already_applied,
    }));
}

export async function getJob(page, ref) {
  await page.goto(ref.url, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
  await sleep(1500);
  // Roles without their own URL: open the card from the list by its title.
  if (ref.url === ref.listUrl) {
    const card = page.getByText(ref.title, { exact: false }).filter({ visible: true }).first();
    if (await card.isVisible().catch(() => false)) {
      await card.click({ timeout: 5000 }).catch(() => {});
      await page.waitForLoadState("networkidle", { timeout: 10000 }).catch(() => {});
      await sleep(1500);
    }
    // Single-page app: the list isn't at a URL, so walk there the way a person would.
    const before = (await readPage(page)).pageText;
    if (!before.includes(ref.title) || before.length < 400) {
      await navigate(page, {
        goal: `Open the details of the role "${ref.title}" (go to the list of opportunities/roles and open it). When its details are on screen, use done with status "none".`,
        profile: loadProfile(),
        mode: "auto",
        maxSteps: 6,
      });
    }
  }
  const expanded = await expandJob(page, "body");
  const { pageText } = await readPage(page); // read after any navigation above
  return {
    ...ref,
    title: ref.title,
    company: "Alignerr",
    location: /remote/i.test(pageText) ? "Remote" : "",
    // The detail text if we got a detail page; otherwise what the card said.
    description: pageText.length > 300 ? pageText : `${ref.title}\n${ref.cardText}\n${pageText}`,
    pageTextLength: pageText.length,
    expanded,
    alreadyApplied: ref.alreadyApplied,
    applyType: "easy",
  };
}

export async function apply(page, job, { resumePath, profile, mode }) {
  return navigate(page, {
    goal:
      `Apply on Alignerr to the role "${job.title}" for her. Open the role if it isn't open yet, click its Apply / Get started / Join button, fill the application (use fill_form for forms, upload_resume when a resume/CV is asked for), go through every step and submit. ` +
      `Finish with done status "applied" when Alignerr confirms the application (or shows it as applied / in review). If the role is already applied, done "already_applied". ` +
      `If the next step is an assessment, test, coding challenge or AI interview, that is hers to take: if the application itself is already submitted use done "applied" with a message saying an assessment is waiting, otherwise need_user.`,
    rules: "On Alignerr, a profile/onboarding step (resume, skills, availability, rate) may come first; complete it with her real data.",
    profile,
    job,
    resumePath,
    mode,
    maxSteps: 35,
  });
}
