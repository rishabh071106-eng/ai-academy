import { expandJob, firstVisible, readPage, textOf } from "./browser.mjs";
import { fillForm } from "./forms.mjs";
import { confirm, humanPause, log, sleep, waitForUser } from "./util.mjs";

export const name = "linkedin";

export async function search(page, s, cfg) {
  const params = new URLSearchParams({ keywords: s.keywords, location: s.location ?? "", sortBy: "DD" });
  if (cfg.easyApplyOnly) params.set("f_AL", "true");
  if (cfg.postedWithinDays) params.set("f_TPR", `r${cfg.postedWithinDays * 86400}`);
  if (s.remote) params.set("f_WT", "2");
  await page.goto(`https://www.linkedin.com/jobs/search/?${params}`, { waitUntil: "domcontentloaded" });
  await sleep(3000);
  if (page.url().includes("/login") || page.url().includes("/authwall")) throw new Error("LinkedIn is not logged in in this Chrome window");

  const ids = new Set();
  for (let round = 0; round < 8 && ids.size < cfg.max; round++) {
    const found = await page.$$eval("[data-occludable-job-id], [data-job-id]", (els) =>
      els.map((e) => e.getAttribute("data-occludable-job-id") || e.getAttribute("data-job-id")).filter((x) => /^\d+$/.test(x)));
    found.forEach((id) => ids.add(id));
    // The results list lazy-loads as it scrolls.
    await page.evaluate(() => {
      const list = document.querySelector(".jobs-search-results-list, .scaffold-layout__list > div, .scaffold-layout__list");
      (list ?? document.scrollingElement).scrollBy(0, 1200);
    });
    await sleep(900);
  }
  return [...ids].slice(0, cfg.max).map((id) => ({ jobId: id, url: `https://www.linkedin.com/jobs/view/${id}/` }));
}

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

  const easy = await page.getByRole("button", { name: /easy apply/i }).first().isVisible({ timeout: 3000 }).catch(() => false);
  const other = !easy && (await page.getByRole("button", { name: /^apply/i }).or(page.getByRole("link", { name: /^apply/i })).first().isVisible().catch(() => false));
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

const modalSel = ".jobs-easy-apply-modal, div[role=dialog][aria-labelledby*='easy-apply' i], div[role=dialog]";

export async function apply(page, job, { resumePath, profile, mode }) {
  const btn = page.getByRole("button", { name: /easy apply/i }).first();
  if (!(await btn.isVisible({ timeout: 5000 }).catch(() => false))) return { status: "needs_attention", note: "Easy Apply button not found" };
  await btn.click();
  const modal = await firstVisible(page, [modalSel], 8000);
  if (!modal) return { status: "needs_attention", note: "Easy Apply dialog did not open" };

  for (let step = 0; step < 15; step++) {
    await humanPause(900, 1600);

    // Upload the tailored resume when the step has a file input for it.
    const file = modal.locator("input[type=file]");
    if ((await file.count()) && resumePath) {
      const accept = (await file.first().getAttribute("accept")) ?? "";
      if (!accept || /pdf/i.test(accept)) {
        await file.first().setInputFiles(resumePath).catch(() => {});
        await sleep(2500);
        log("dim", "   ↳ uploaded tailored resume");
      }
    }

    const unanswered = await fillForm(modal, profile, job);
    if (unanswered.length) {
      log("warn", `   Couldn't answer: ${unanswered.map((f) => `"${f.label}"`).join(", ")}`);
      if (mode === "auto") return discard(page, "Unanswered: " + unanswered.map((f) => f.label).join("; "));
      const go = await waitForUser(`Couldn't answer ${unanswered.map((f) => `"${f.label}"`).join(", ")} for ${job.company}. Fill it in the Chrome dialog, then continue.`);
      if (!go) return discard(page, "Skipped by you at questions", "skipped");
    }

    const submit = await firstVisible(modal, ["button[aria-label='Submit application']", "button:has-text('Submit application')"]);
    if (submit) {
      // Don't auto-follow the company.
      const follow = modal.locator("input#follow-company-checkbox");
      if (await follow.isChecked().catch(() => false)) await modal.locator("label[for=follow-company-checkbox]").click().catch(() => {});
      if (mode !== "auto") {
        if (!(await confirm(`Submit application to ${job.company} – ${job.title}?`))) return discard(page, "You chose not to submit", "skipped");
      }
      await submit.click();
      const done = await firstVisible(page, ["text=/application (was )?sent/i", "h3:has-text('Application sent')"], 10000);
      await firstVisible(page, ["button[aria-label='Dismiss']"], 3000).then((b) => b?.click()).catch(() => {});
      return done ? { status: "applied", note: "Easy Apply" } : { status: "needs_attention", note: "Clicked submit but no confirmation seen — check LinkedIn > My jobs" };
    }

    const next = await firstVisible(modal, [
      "button[aria-label='Continue to next step']", "button[aria-label='Review your application']",
      "button:has-text('Next')", "button:has-text('Review')", "button:has-text('Continue')",
    ]);
    if (!next) return discard(page, "No Next/Submit button in the dialog");
    await next.click();
    await sleep(1200);
    const err = await firstVisible(modal, [".artdeco-inline-feedback--error", "[data-test-form-element-error-messages]"]);
    if (err && step > 0) {
      const msg = (await err.innerText()).trim();
      log("warn", `   Form error: ${msg}`);
      if (mode === "auto") return discard(page, "Form error: " + msg);
      await waitForUser(`Form error on ${job.company}: "${msg}". Fix it in Chrome, then continue.`, { allowSkip: false });
    }
  }
  return discard(page, "Too many steps in Easy Apply");
}

async function discard(page, note, status = "needs_attention") {
  const close = await firstVisible(page, ["button[aria-label='Dismiss']"]);
  await close?.click().catch(() => {});
  const discardBtn = await firstVisible(page, ["button[data-control-name='discard_application_confirm_btn']", "button:has-text('Discard')"], 3000);
  await discardBtn?.click().catch(() => {});
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
