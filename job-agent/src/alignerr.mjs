// Alignerr (app.alignerr.com): AI-training / expert roles. The agent lists the open roles
// on the home page, reads each one, scores it against her resume, and applies with the
// tailored resume. Skill assessments and AI interviews are for her to take herself, so those
// are handed over (fully automatic mode marks them "needs attention" and moves on).
import { expandJob, firstVisible, readPage } from "./browser.mjs";
import { applyHere, handOver } from "./external.mjs";
import { humanPause, log, sleep } from "./util.mjs";

export const name = "alignerr";
const HOME = "https://app.alignerr.com/home";

async function loggedIn(page) {
  return !/\/(login|signin|sign-in|auth)\b/i.test(page.url()) && !(await page.getByRole("button", { name: /^(log ?in|sign ?in|continue with google)$/i }).filter({ visible: true }).count().catch(() => 0));
}

export async function search(page, s, cfg) {
  if (cfg.pageIndex) return []; // one listing
  await page.goto(cfg.url || HOME, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
  await sleep(2500);
  if (!(await loggedIn(page))) throw new Error("Alignerr is not logged in in this Chrome window — log in once at app.alignerr.com");

  // Open "browse / all opportunities" if the home page only shows a few.
  const browse = page.getByRole("link", { name: /browse|all (jobs|opportunities|roles)|view all|explore/i }).or(page.getByRole("button", { name: /browse|all (jobs|opportunities|roles)|view all|explore/i })).filter({ visible: true }).first();
  if (await browse.isVisible().catch(() => false)) {
    await browse.click().catch(() => {});
    await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
    await sleep(2000);
  }
  // Lazy-loaded lists.
  for (let i = 0; i < 6; i++) {
    await page.mouse.wheel(0, 1500).catch(() => {});
    await sleep(500);
  }
  const jobs = await page.evaluate(() => {
    const out = new Map();
    for (const a of document.querySelectorAll("a[href]")) {
      const href = a.href;
      if (!/alignerr\.com/.test(href) || !/\/(jobs?|opportunit\w*|positions?|projects?|roles?|listings?)\/[\w-]+/i.test(href)) continue;
      const card = a.closest("li, article, [class*=card], [class*=Card], div") || a;
      const text = (card.innerText || a.innerText || "").replace(/\s+/g, " ").trim().slice(0, 400);
      const id = href.split("?")[0].replace(/\/$/, "").split("/").pop();
      if (id && !out.has(id)) out.set(id, { jobId: id, url: href.split("#")[0], cardText: text });
    }
    return [...out.values()];
  });
  const kw = (s.keywords || "").toLowerCase().split(/\s+/).filter(Boolean);
  const filtered = kw.length ? jobs.filter((j) => kw.some((k) => j.cardText.toLowerCase().includes(k))) : jobs;
  log("dim", `  Alignerr lists ${jobs.length} roles${kw.length ? `, ${filtered.length} match "${s.keywords}"` : ""}`);
  return filtered.slice(0, cfg.max || 60);
}

export async function getJob(page, ref) {
  await page.goto(ref.url, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
  await humanPause(1200, 2000);
  const expanded = await expandJob(page, "body");
  const { docTitle, h1, pageText } = await readPage(page);
  const heading = h1 || (await page.locator("h2").first().innerText({ timeout: 1000 }).catch(() => "")) || docTitle.replace(/\s*[|–-]\s*Alignerr.*$/i, "");
  const applyBtn = await firstVisible(page, ["button:has-text('Apply')", "a:has-text('Apply')", "button:has-text('Start application')", "button:has-text('Get started')"]);
  return {
    ...ref,
    title: heading.trim(),
    company: "Alignerr",
    location: /remote/i.test(pageText) ? "Remote" : "",
    description: pageText,
    pageTextLength: pageText.length,
    expanded,
    alreadyApplied: /\b(applied|application (submitted|received|under review|in review)|you('ve| have) applied)\b/i.test(pageText.slice(0, 4000)) && !applyBtn,
    applyType: applyBtn ? "easy" : "none",
  };
}

export async function apply(page, job, { resumePath, profile, mode }) {
  const result = await applyHere(page, job, { resumePath, profile, mode, label: "Alignerr" });
  // Assessments / AI interviews after applying are hers to take; record that clearly.
  const body = await page.locator("body").innerText().catch(() => "");
  if (result.status !== "applied" && /assessment|skills? test|ai interview|start (the )?interview|record (a|your) video|take (the )?test/i.test(body)) {
    const r = await handOver(page, job, mode, "this role needs an assessment or interview that you take yourself", false);
    return r ?? { status: "needs_attention", note: "Alignerr: assessment/interview for you to take" };
  }
  if (result.status === "applied" && /assessment|ai interview/i.test(body)) {
    return { ...result, note: "Applied on Alignerr — next step is an assessment/interview for you to take" };
  }
  return result;
}
