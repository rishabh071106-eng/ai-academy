import { expandJob, firstVisible, readPage, textOf } from "./browser.mjs";
import { fillForm } from "./forms.mjs";
import fs from "node:fs";
import path from "node:path";
import { ask, confirm, DATA_DIR, humanPause, log, sleep, waitForUser } from "./util.mjs";

export const name = "linkedin";

export async function search(page, s, cfg) {
  const params = new URLSearchParams({ keywords: s.keywords, location: s.location ?? "", sortBy: "DD" });
  if (cfg.easyApplyOnly) params.set("f_AL", "true");
  if (cfg.postedWithinDays) params.set("f_TPR", `r${cfg.postedWithinDays * 86400}`);
  if (s.remote) params.set("f_WT", "2");
  await page.goto(`https://www.linkedin.com/jobs/search/?${params}`, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("load", { timeout: 15000 }).catch(() => {});
  await sleep(3000);
  if (/\/login|\/authwall|\/checkpoint/.test(page.url())) throw new Error("LinkedIn is not logged in in this Chrome window");

  // LinkedIn sometimes ignores URL keywords and shows "recommended" jobs; then type the search in.
  const box = page.getByRole("combobox", { name: /title|skill|search/i }).or(page.getByRole("textbox", { name: /title|skill|search jobs/i })).filter({ visible: true }).first();
  const current = (await box.inputValue({ timeout: 3000 }).catch(() => null)) ?? "";
  if (!current.toLowerCase().includes(s.keywords.toLowerCase().split(/\s+/)[0])) {
    log("dim", `  LinkedIn didn't apply the search ("${current}"); typing "${s.keywords}"`);
    await box.fill(s.keywords).catch(() => {});
    const loc = page.getByRole("combobox", { name: /city|location|state|zip/i }).filter({ visible: true }).first();
    if (s.location) await loc.fill(s.location).catch(() => {});
    await box.press("Enter").catch(() => {});
    await sleep(4000);
  }
  log("dim", `  LinkedIn shows: ${(await page.title()).replace(/\s*\|\s*LinkedIn$/, "")}`);

  const jobs = new Map();
  for (let round = 0; round < 10 && jobs.size < cfg.max; round++) {
    const found = await page.evaluate(() => {
      const out = [];
      const add = (id, el) => id && /^\d+$/.test(id) && out.push({ id, text: (el?.innerText || "").replace(/\s+/g, " ").trim().slice(0, 300) });
      document.querySelectorAll("[data-occludable-job-id], [data-job-id]").forEach((e) => add(e.getAttribute("data-occludable-job-id") || e.getAttribute("data-job-id"), e));
      document.querySelectorAll("a[href*='/jobs/view/'], a[href*='currentJobId=']").forEach((a) => {
        const id = a.href.match(/jobs\/view\/(\d+)/)?.[1] || a.href.match(/currentJobId=(\d+)/)?.[1];
        add(id, a.closest("li, [data-occludable-job-id], div[class*=card]") || a);
      });
      return out;
    });
    for (const f of found) if (!jobs.has(f.id) || (!jobs.get(f.id) && f.text)) jobs.set(f.id, f.text);
    // The results list lazy-loads as it scrolls.
    await page.evaluate(() => {
      const list = document.querySelector(".jobs-search-results-list, .scaffold-layout__list > div, .scaffold-layout__list, [class*=results-list]");
      (list ?? document.scrollingElement).scrollBy(0, 1200);
    });
    await sleep(900);
  }
  return [...jobs].slice(0, cfg.max).map(([id, cardText]) => ({ jobId: id, url: `https://www.linkedin.com/jobs/view/${id}/`, cardText }));
}

// LinkedIn renders Easy Apply as a <button> on some layouts and as a link on others.
// There are often two (one hidden in a sticky header); always take a visible one.
const easyApplyControl = (page) => page.getByRole("button", { name: /easy apply/i }).or(page.getByRole("link", { name: /easy apply/i })).filter({ visible: true }).first();

export async function getJob(page, ref) {
  await page.goto(ref.url, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("load", { timeout: 15000 }).catch(() => {});
  await firstVisible(page, ["h1", "main"], 10000);
  await humanPause(1500, 2500);
  const expanded = await expandJob(page);

  const { docTitle, h1, pageText } = await readPage(page);
  // The tab title is "<job title> | <company> | LinkedIn" (sometimes with a "(3) " prefix).
  const parts = docTitle.replace(/^\(\d+\)\s*/, "").split(/\s+\|\s+/);
  const fromTitle = parts.length >= 3 && /linkedin/i.test(parts.at(-1)) ? { title: parts[0], company: parts[1] } : {};

  const description = await textOf(page, ["#job-details", ".jobs-description__content", ".jobs-box__html-content", "[class*=jobs-description]"]);
  const company = (await textOf(page, [".job-details-jobs-unified-top-card__company-name a", ".job-details-jobs-unified-top-card__company-name", ".jobs-unified-top-card__company-name"])).split("\n")[0];

  const easy = await easyApplyControl(page).isVisible({ timeout: 3000 }).catch(() => false);
  const other = !easy && (await page.getByRole("button", { name: /^apply/i }).or(page.getByRole("link", { name: /^apply/i })).filter({ visible: true }).first().isVisible().catch(() => false));
  return {
    ...ref,
    title: h1 || fromTitle.title || "",
    company: company || fromTitle.company || "",
    location: (await textOf(page, [".job-details-jobs-unified-top-card__primary-description-container", ".job-details-jobs-unified-top-card__tertiary-description-container"])).split("·")[0].trim(),
    // Fall back to the whole page text when the description block isn't found.
    description: description.length > 300 ? description : pageText,
    pageTextLength: pageText.length,
    expanded,
    hiringContact: await hiringContact(page),
    alreadyApplied: /\bApplied\s+\d+\s*(minute|hour|day|week|month)s?\s+ago\b|Application submitted/i.test(pageText.slice(0, 3000)),
    applyType: easy ? "easy" : other ? "external" : "none",
  };
}

/** The "Meet the hiring team" card, if the job shows one. */
async function hiringContact(page) {
  return page.evaluate(() => {
    const heading = [...document.querySelectorAll("h2, h3, span")].find((el) => /meet the hiring team|people you can reach out to/i.test(el.textContent || ""));
    // Walk up from the heading to the nearest block that contains a profile link.
    let box = heading ?? null;
    for (let i = 0; box && i < 6 && !box.querySelector?.("a[href*='/in/']"); i++) box = box.parentElement;
    const link = box?.querySelector("a[href*='/in/']");
    if (!link) return null;
    box.setAttribute("data-ja", "hiring-team");
    const lines = (link.closest("[class*=hirer], li, div")?.innerText || link.innerText).split("\n").map((t) => t.trim()).filter(Boolean);
    const name = (link.querySelector("strong, span[aria-hidden=true]")?.innerText || lines[0] || "").trim();
    return {
      name: name.replace(/\s*\(.*?\)\s*$/, "").replace(/\s+/g, " "),
      title: lines.find((t) => t !== name && t.length > 12 && !/^(\d|·|job poster|message|connect)/i.test(t)) || "",
      profileUrl: link.href.split("?")[0],
    };
  }).catch(() => null);
}

/**
 * Sends `text` to the job poster through the "Message" button on the hiring-team card.
 * LinkedIn only allows this for connections, open profiles or Premium (InMail) users, so
 * it often isn't possible; then the message just stays as a draft on the dashboard.
 */
export async function messageHiringTeam(page, job, msg, { mode, autoSend }) {
  const box = page.locator("[data-ja=hiring-team]").first();
  const btn = (await box.count()) ? await firstVisible(box, ["button:has-text('Message')", "a:has-text('Message')"]) : null;
  if (!btn) return { status: "draft", note: "No Message button on the hiring-team card" };
  if (mode === "auto" && !autoSend) return { status: "draft", note: "Auto-send is off; send it from the dashboard" };

  await btn.click();
  // With Premium the composer opens as an InMail (it may also show "InMail credits"); only give up
  // when no text box appears at all.
  const box2 = await firstVisible(page, [".msg-form__contenteditable", "div[role=textbox][contenteditable=true]"], 8000);
  if (!box2) {
    const upsell = await firstVisible(page, ["text=/try premium|reactivate premium|buy inmail|out of inmail/i"], 500);
    await firstVisible(page, ["button[aria-label='Dismiss']", "button[aria-label*='Close' i]"]).then((b) => b?.click()).catch(() => {});
    return { status: "draft", note: upsell ? "LinkedIn needs Premium / more InMail credits to message this person" : "Message window didn't open" };
  }
  const subject = await firstVisible(page, ["input[name=subject]", "input[placeholder*='Subject' i]", "input[aria-label*='Subject' i]"]);
  if (subject && msg.subject) await subject.fill(msg.subject);
  await box2.click();
  // Type paragraph by paragraph; Shift+Enter makes a new line without sending.
  const paras = String(msg.full).split(/\n+/);
  for (let i = 0; i < paras.length; i++) {
    await box2.pressSequentially(paras[i], { delay: 6 });
    if (i < paras.length - 1) {
      await page.keyboard.press("Shift+Enter");
      await page.keyboard.press("Shift+Enter");
    }
  }

  const send = mode === "auto" || mode === "send" ? true : await confirm(`Send this message to ${job.hiringContact?.name || "the hiring team"} at ${job.company}? (you can edit it in Chrome first)`);
  const close = async () => {
    const c = await firstVisible(page, ["button:has-text('Close your conversation')", ".msg-overlay-bubble-header__controls button[aria-label*='Close' i]"]);
    await c?.click().catch(() => {});
    const discard = await firstVisible(page, ["button:has-text('Discard')"], 1500);
    await discard?.click().catch(() => {});
  };
  if (!send) {
    await close();
    return { status: "draft", note: "You chose not to send" };
  }
  const sendBtn = await firstVisible(page, ["button.msg-form__send-button", "button[type=submit]:has-text('Send')", "button:has-text('Send')"]);
  if (!sendBtn) {
    await close();
    return { status: "draft", note: "Send button not found" };
  }
  await sendBtn.click();
  await sleep(1500);
  await close();
  return { status: "sent", note: `Sent to ${job.hiringContact?.name || "hiring team"} on LinkedIn` };
}

/**
 * After clicking Easy Apply, LinkedIn shows the form either in a dialog (sometimes inside a
 * shadow root) or on its own /apply page. Returns a locator for whichever appeared.
 */
async function applyRoot(page) {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    const dialog = page.getByRole("dialog").filter({ has: page.locator("input, select, textarea, button") }).filter({ hasText: /apply|contact info|resume|mobile|phone|email|question|review|submit/i }).last();
    if (await dialog.isVisible().catch(() => false)) return dialog;
    if (/\/apply\b|openSDUIApplyFlow/i.test(page.url())) {
      const main = page.locator("main").first();
      if (await main.locator("input, select, textarea").first().isVisible().catch(() => false)) return main;
    }
    await sleep(400);
  }
  return null;
}

const button = (root, re) => root.getByRole("button", { name: re }).filter({ visible: true }).first();

export async function apply(page, job, { resumePath, profile, mode }) {
  const ctl = easyApplyControl(page);
  await ctl.waitFor({ state: "visible", timeout: 8000 }).catch(() => {});
  if (!(await ctl.isVisible().catch(() => false))) return stuck(page, null, job, mode, "I can't see the Easy Apply button");
  await ctl.scrollIntoViewIfNeeded().catch(() => {});
  await ctl.click();
  const root = await applyRoot(page);
  if (!root) return stuck(page, null, job, mode, "the Easy Apply form didn't open");
  log("dim", "   Easy Apply form opened");

  let lastStep = "";
  let sameStepCount = 0;
  for (let step = 0; step < 15; step++) {
    await humanPause(900, 1500);
    const heading = ((await root.locator("h3, h2").first().innerText({ timeout: 1000 }).catch(() => "")) || "").trim().split("\n")[0];
    log("dim", `   step ${step + 1}${heading ? `: ${heading}` : ""}`);

    // Upload the tailored resume when the step has a file input for it.
    const file = root.locator("input[type=file]");
    if ((await file.count().catch(() => 0)) && resumePath) {
      const accept = (await file.first().getAttribute("accept").catch(() => "")) ?? "";
      if (!accept || /pdf/i.test(accept)) {
        await file.first().setInputFiles(resumePath).then(() => log("dim", "   ↳ uploaded tailored resume")).catch((e) => log("warn", `   resume upload failed: ${e.message.split("\n")[0]}`));
        await sleep(2500);
      }
    }

    let unanswered = await fillForm(root, profile, job);
    if (unanswered.length) {
      log("warn", `   couldn't answer: ${unanswered.map((f) => `"${f.label}"`).join(", ")}`);
      if (mode === "auto") return discard(page, "Unanswered: " + unanswered.map((f) => f.label).join("; "));
      const go = await waitForUser(`${job.company}: please fill ${unanswered.map((f) => `"${f.label}"`).join(", ")} in the Chrome form, then press Done.`);
      if (!go) return discard(page, "Skipped by you at questions", "skipped");
    }

    const submit = button(root, /submit application|^submit$/i);
    if (await submit.isVisible().catch(() => false)) {
      // Don't auto-follow the company.
      const follow = root.getByRole("checkbox", { name: /follow/i }).first();
      if (await follow.isChecked().catch(() => false)) await follow.uncheck({ force: true }).catch(() => {});
      if (mode !== "auto" && !(await confirm(`Submit application to ${job.company} – ${job.title}?`))) return discard(page, "You chose not to submit", "skipped");
      await submit.click();
      const done = await firstVisible(page, ["text=/application (was )?(sent|submitted)/i", "text=/your application was sent/i"], 12000);
      await button(page, /dismiss|done|close/i).click({ timeout: 3000 }).catch(() => {});
      return done ? { status: "applied", note: "Easy Apply" } : { status: "needs_attention", note: "Clicked submit but no confirmation seen — check LinkedIn > My jobs" };
    }

    const next = [button(root, /review/i), button(root, /next|continue/i)];
    let clicked = false;
    for (const b of next) {
      if (await b.isVisible().catch(() => false)) {
        await b.click();
        clicked = true;
        break;
      }
    }
    if (!clicked) {
      const r = await stuck(page, root, job, mode, "there's no Next / Review / Submit button on this step", true);
      if (r) return r;
      continue;
    }
    await sleep(1500);

    // Validation errors keep us on the same step: fill again once, then ask for help.
    const err = root.locator(".artdeco-inline-feedback--error, [data-test-form-element-error-messages], [role=alert]").filter({ hasText: /\S/ }).first();
    if (await err.isVisible().catch(() => false)) {
      const msg = (await err.innerText().catch(() => "")).trim().split("\n")[0];
      log("warn", `   form says: ${msg}`);
      unanswered = await fillForm(root, profile, job);
      const again = await button(root, /review|next|continue|submit application/i);
      if (!unanswered.length && (await again.isVisible().catch(() => false)) && !/submit/i.test((await again.innerText().catch(() => "")) || "")) {
        await again.click();
        await sleep(1500);
      }
      if (await err.isVisible().catch(() => false)) {
        const r = await stuck(page, root, job, mode, `the form says "${msg}"`, true);
        if (r) return r;
        continue;
      }
    }
    // Guard against looping on a step that never advances.
    sameStepCount = heading && heading === lastStep ? sameStepCount + 1 : 0;
    lastStep = heading;
    if (sameStepCount >= 2) {
      sameStepCount = 0;
      const r = await stuck(page, root, job, mode, "the form isn't moving to the next step", true);
      if (r) return r;
    }
  }
  return stuck(page, root, job, mode, "too many steps");
}

/**
 * The agent couldn't finish an application. Save a screenshot for debugging; in review mode
 * hand over to the user instead of silently moving on.
 */
async function stuck(page, root, job, mode, reason, canContinue = false) {
  const shot = path.join(DATA_DIR, "debug", `linkedin-${job.jobId}-apply.png`);
  fs.mkdirSync(path.dirname(shot), { recursive: true });
  await page.screenshot({ path: shot }).catch(() => {});
  if (root) fs.writeFileSync(shot.replace(/\.png$/, ".html"), await root.innerHTML().catch(() => ""));
  log("warn", `   stuck: ${reason} (screenshot: data/debug/${path.basename(shot)})`);
  if (mode === "auto") return discard(page, `Stuck: ${reason}`);
  const choices = [
    ...(canContinue ? [{ label: "I fixed it, continue", value: "" }] : []),
    { label: "I submitted it myself", value: "done" },
    { label: "Skip this job", value: "s" },
  ];
  const r = await ask(`${job.company} – ${job.title}: I'm stuck because ${reason}. ${canContinue ? "Fix it in the Chrome form and I'll carry on, " : ""}finish it yourself, or skip it.`, choices);
  if (r === "done") return { status: "applied", note: "Submitted by you after the agent got stuck" };
  if (r === "" && canContinue) return null;
  return discard(page, `Stuck: ${reason}`);
}

async function discard(page, note, status = "needs_attention") {
  await button(page, /dismiss|close/i).click({ timeout: 2000 }).catch(() => {});
  await button(page, /^discard$/i).click({ timeout: 3000 }).catch(() => {});
  return { status, note };
}

/** Opens a job again and sends (the possibly edited) message to its hiring contact. */
export async function sendForJob(page, row) {
  await page.goto(row.url, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("load", { timeout: 15000 }).catch(() => {});
  await expandJob(page);
  const contact = await hiringContact(page);
  if (!contact) return { status: "draft", note: "This job has no hiring-team card to message" };
  return messageHiringTeam(page, { ...row, hiringContact: contact }, row.hiringMessage, { mode: "send" });
}
