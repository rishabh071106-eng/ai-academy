// A generic job portal (Indeed, Foundit, Shine, TimesJobs, Glassdoor, Hirist, Instahyre,
// Cutshort, Wellfound, Apna, Adzuna, Jooble…) driven by the AI navigator: it makes sure she
// has an account (Google sign-in, or create / recover one with her email and ATS_PASSWORD,
// codes read from Gmail), runs each search, lists the jobs on the results page, reads every
// job and applies the way a person would. Configured in config.json under platforms.<key>
// with type "portal", home, searchUrl ({keywords}/{location} placeholders) and searches.
import { expandJob, readPage } from "./browser.mjs";
import { applyHere } from "./external.mjs";
import { ensureAccount, looksLoggedOut } from "./login.mjs";
import { GOOGLE_RULES, navigate } from "./navigator.mjs";
import { loadProfile, log, sleep } from "./util.mjs";

const BLOCKED = /just a moment|checking your browser|verify you are (a )?human|access denied|unusual traffic|attention required|cloudflare|are you a robot|ddos-guard|captcha/i;

/** Loads `url` without hanging on slow pages; returns "blocked" when the site shows a bot check. */
async function open(page, url) {
  await page.goto(url, { waitUntil: "commit", timeout: 25000 });
  await page.waitForLoadState("domcontentloaded", { timeout: 20000 }).catch(() => {});
  await page.waitForLoadState("networkidle", { timeout: 8000 }).catch(() => {});
  const head = await page.evaluate(() => `${document.title}\n${(document.body?.innerText || "").slice(0, 1200)}`).catch(() => "");
  if (BLOCKED.test(head) && head.length < 1500) {
    // Give an automatic check a moment to pass by itself.
    await sleep(8000);
    const again = await page.evaluate(() => `${document.title}\n${(document.body?.innerText || "").slice(0, 1200)}`).catch(() => "");
    if (BLOCKED.test(again) && again.length < 1500) return "blocked";
  }
  return "ok";
}

const hash = (s) => {
  let h = 0;
  for (const c of String(s)) h = (h * 31 + c.charCodeAt(0)) | 0;
  return Math.abs(h).toString(36);
};

export function makePortal(key, cfg) {
  const site = cfg.label || key[0].toUpperCase() + key.slice(1);
  const home = cfg.home;
  const isLoggedIn = async (page) => !(await looksLoggedOut(page));

  async function ready(page) {
    if (cfg.requiresLogin === false) return true;
    const ok = await ensureAccount(page, site, { isLoggedIn, home });
    if (!ok && cfg.requiresLogin === true) throw new Error(`${site}: not logged in`);
    return ok;
  }

  let blockedRound = 0;
  async function search(page, s, c) {
    if (c.pageIndex > 0 && !cfg.pagination) return []; // one results page unless the site paginates by URL
    if (blockedRound >= 2) throw new Error(`${site} is showing a bot check on every page — skipping it for now`);
    const loc = s.location ?? cfg.location ?? "";
    let url = cfg.searchUrl
      ? cfg.searchUrl.replace("{keywords}", encodeURIComponent(s.keywords)).replace("{location}", encodeURIComponent(loc)).replace("{keywords-slug}", s.keywords.toLowerCase().replace(/[^a-z0-9]+/g, "-")).replace("{location-slug}", loc.toLowerCase().replace(/[^a-z0-9]+/g, "-")).replace("{page}", String((c.pageIndex ?? 0) + 1))
      : home;
    const state = await open(page, url);
    if (state === "blocked") {
      blockedRound++;
      throw new Error(`${site} is showing a bot check ("just a moment / verify you are human") instead of the page`);
    }
    blockedRound = 0;
    await ready(page);
    if (page.url() !== url && !page.url().startsWith(url.split("?")[0])) await page.goto(url, { waitUntil: "domcontentloaded" }).catch(() => {});
    const profile = loadProfile();
    const r = await navigate(page, {
      goal: `On ${site}, list the job postings for "${s.keywords}"${loc ? ` in ${loc}` : ""}. If this page already shows a list of job results, use report_jobs right away with EVERY job on the page: title, the id of the job's link (target) so its URL is known, and a one-line summary (company, location, posted when). If the page shows no results, use the site's search box (type the keywords${loc ? ` and the location "${loc}"` : ""}, press Enter) and then report_jobs. Close pop-ups that block the page. Never apply from here.`,
      rules: GOOGLE_RULES(profile.email),
      profile,
      mode: "auto",
      maxSteps: 10,
      stopOnReport: true,
    });
    const jobs = (r.jobs ?? []).filter((j) => j.href && !j.already_applied).map((j) => ({ jobId: hash(j.href.split("#")[0]), url: j.href, cardText: `${j.title} · ${j.summary || ""}`, title: j.title }));
    log("dim", `  ${site}: ${jobs.length} job links on the results page`);
    return jobs.slice(0, c.max ?? 60);
  }

  async function getJob(page, ref) {
    if ((await open(page, ref.url)) === "blocked") throw new Error(`${site} is showing a bot check instead of the job page`);
    await sleep(800);
    const expanded = await expandJob(page, "body");
    const { docTitle, h1, pageText } = await readPage(page);
    const title = h1 || ref.title || docTitle.split(/[|\-–]/)[0].trim();
    return {
      ...ref,
      title,
      company: "",
      location: "",
      description: pageText,
      pageTextLength: pageText.length,
      expanded,
      alreadyApplied: /\b(you('ve| have) (already )?applied|application (sent|submitted)|applied on \w+ \d|already applied)\b/i.test(pageText.slice(0, 4000)),
      closed: /no longer accepting|this job (is|has) (closed|expired)|job (has )?expired|position (has been )?filled|no longer available/i.test(pageText.slice(0, 4000)),
      applyType: "easy",
    };
  }

  async function apply(page, job, { resumePath, profile, mode, coverLetter }) {
    await ready(page).catch(() => {});
    return applyHere(page, job, { resumePath, profile, mode, coverLetter, label: site, navigatorFirst: true, rules: `${GOOGLE_RULES(profile.email)}\n- If ${site} redirects to the company's own site to apply, carry on there (new tabs included) and complete that application.\n- If ${site} asks to complete her profile before applying, fill it from her data (upload_resume, fill_form) and continue to the application.` });
  }

  return { name: key, site, search, getJob, apply };
}
