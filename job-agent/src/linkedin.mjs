import { firstVisible, textOf } from "./browser.mjs";
import { fillForm } from "./forms.mjs";
import { ask, humanPause, log, sleep } from "./util.mjs";

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
  await firstVisible(page, ["h1"], 10000);
  await humanPause();
  // Expand "See more" on the description.
  const more = await firstVisible(page, ["button.jobs-description__footer-button", "button[aria-label*='see more' i]"]);
  await more?.click().catch(() => {});

  const top = (await textOf(page, [".job-details-jobs-unified-top-card__container--two-pane", ".jobs-unified-top-card", "main"])) || "";
  const applyBtn = await firstVisible(page, ["button.jobs-apply-button", "button[aria-label*='Apply to' i]", "a[aria-label*='Apply' i]"], 4000);
  const applyLabel = applyBtn ? ((await applyBtn.getAttribute("aria-label")) || (await applyBtn.innerText())) : "";
  return {
    ...ref,
    title: await textOf(page, ["h1"]),
    company: await textOf(page, [".job-details-jobs-unified-top-card__company-name a", ".job-details-jobs-unified-top-card__company-name", ".jobs-unified-top-card__company-name"]),
    location: (await textOf(page, [".job-details-jobs-unified-top-card__primary-description-container", ".job-details-jobs-unified-top-card__tertiary-description-container", ".jobs-unified-top-card__bullet"])).split("·")[0].trim(),
    description: await textOf(page, ["#job-details", ".jobs-description__content", ".jobs-box__html-content", "article"]),
    alreadyApplied: /\bApplied\b.*\bago\b|Application submitted/i.test(top),
    applyType: !applyBtn ? "none" : /easy apply/i.test(applyLabel) ? "easy" : "external",
  };
}

const modalSel = ".jobs-easy-apply-modal, div[role=dialog][aria-labelledby*='easy-apply' i], div[role=dialog]";

export async function apply(page, job, { resumePath, profile, mode }) {
  const btn = await firstVisible(page, ["button.jobs-apply-button", "button[aria-label*='Easy Apply' i]"], 5000);
  if (!btn) return { status: "needs_attention", note: "Easy Apply button not found" };
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
      const r = await ask("Fill those in the Chrome dialog, then press Enter (or type s to skip this job):");
      if (r.toLowerCase() === "s") return discard(page, "Skipped by you at questions", "skipped");
    }

    const submit = await firstVisible(modal, ["button[aria-label='Submit application']", "button:has-text('Submit application')"]);
    if (submit) {
      // Don't auto-follow the company.
      const follow = modal.locator("input#follow-company-checkbox");
      if (await follow.isChecked().catch(() => false)) await modal.locator("label[for=follow-company-checkbox]").click().catch(() => {});
      if (mode !== "auto") {
        const r = await ask(`Submit application to ${job.company} – ${job.title}? [Y/n]`);
        if (/^n/i.test(r)) return discard(page, "You chose not to submit", "skipped");
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
      await ask("Fix it in Chrome and press Enter:");
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
