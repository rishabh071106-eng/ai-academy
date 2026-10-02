// Applies on the company's own careers site when a LinkedIn / Naukri job says
// "Apply on company website". Workday gets a dedicated flow (sign in / create account,
// multi-step wizard); Greenhouse, Lever, Ashby, SmartRecruiters and ordinary one-page
// forms go through the generic filler. CAPTCHAs and email verification are always handed
// to the user — the agent never tries to get around them.
import fs from "node:fs";
import path from "node:path";
import { fillCustomSelects, fillForm } from "./forms.mjs";
import { ask, confirm, DATA_DIR, humanPause, log, sleep } from "./util.mjs";

const SUCCESS = /thank you for (applying|your application|your interest)|application (has been |was )?(received|submitted|sent|complete)|we('ve| have) received your application|successfully (applied|submitted)|you('ve| have) applied/i;

export function detectAts(url) {
  const u = url.toLowerCase();
  if (/myworkdayjobs\.com|\.workday\.com|wd\d+\.myworkday/.test(u)) return "workday";
  if (/greenhouse\.io/.test(u)) return "greenhouse";
  if (/lever\.co/.test(u)) return "lever";
  if (/ashbyhq\.com/.test(u)) return "ashby";
  if (/smartrecruiters\.com/.test(u)) return "smartrecruiters";
  if (/icims\.com/.test(u)) return "icims";
  if (/taleo\.net|oraclecloud\.com/.test(u)) return "oracle";
  if (/successfactors|sapsf/.test(u)) return "successfactors";
  return "generic";
}

const btn = (root, re) => root.getByRole("button", { name: re }).or(root.getByRole("link", { name: re })).filter({ visible: true }).first();
const visible = (loc) => loc.isVisible().catch(() => false);

async function dismissBanners(page) {
  for (const re of [/accept all|accept cookies|^accept$|i agree|got it|allow all/i]) {
    const b = page.getByRole("button", { name: re }).filter({ visible: true }).first();
    if (await visible(b)) await b.click({ timeout: 1500 }).catch(() => {});
  }
}

async function captchaPresent(page) {
  return page
    .locator("iframe[src*='recaptcha'], iframe[src*='hcaptcha'], iframe[title*='captcha' i], iframe[src*='challenges.cloudflare'], #px-captcha")
    .filter({ visible: true })
    .count()
    .then((n) => n > 0)
    .catch(() => false);
}

async function handOver(page, job, mode, reason, canContinue = true) {
  const shot = path.join(DATA_DIR, "debug", `site-${job.platform}-${job.jobId}.png`);
  fs.mkdirSync(path.dirname(shot), { recursive: true });
  await page.screenshot({ path: shot, fullPage: true }).catch(() => {});
  log("warn", `   company site: ${reason} (screenshot: data/debug/${path.basename(shot)})`);
  if (mode === "auto") return { status: "needs_attention", note: `Company site: ${reason}` };
  await page.bringToFront().catch(() => {});
  const r = await ask(`${job.company} (company site): ${reason}. ${canContinue ? "Do it in Chrome and I'll carry on, " : ""}finish it yourself, or skip.`, [
    ...(canContinue ? [{ label: "Done, continue", value: "" }] : []),
    { label: "I submitted it myself", value: "done" },
    { label: "Skip this job", value: "s" },
  ]);
  if (r === "done") return { status: "applied", note: "Submitted by you on the company site" };
  if (r === "" && canContinue) return null;
  return { status: "needs_attention", note: `Company site: ${reason}` };
}

/** Upload the tailored resume into every resume/CV file input on the page. */
async function uploadResume(root, resumePath) {
  if (!resumePath) return false;
  const inputs = root.locator("input[type=file]");
  const n = await inputs.count().catch(() => 0);
  let done = false;
  for (let i = 0; i < n; i++) {
    const inp = inputs.nth(i);
    const meta = await inp.evaluate((el) => {
      const near = el.closest("div, section, fieldset")?.innerText || "";
      return `${el.name} ${el.id} ${el.getAttribute("aria-label") || ""} ${el.getAttribute("data-automation-id") || ""} ${near.slice(0, 200)}`.toLowerCase();
    }).catch(() => "");
    const hasFile = await inp.evaluate((el) => el.files?.length > 0).catch(() => false);
    if (hasFile || /cover/.test(meta) && !/resume|cv/.test(meta)) continue;
    if (n === 1 || /resume|cv|curriculum|file-upload|attach/.test(meta)) {
      await inp.setInputFiles(resumePath).then(() => (done = true)).catch(() => {});
    }
  }
  if (done) {
    log("dim", "   ↳ uploaded tailored resume");
    await sleep(3000); // sites parse the resume and prefill fields
  }
  return done;
}

async function fillCoverLetter(root, coverLetter) {
  if (!coverLetter) return;
  const ta = root.getByLabel(/cover letter|additional information|message to (the )?hiring/i).filter({ visible: true }).first();
  if ((await visible(ta)) && !(await ta.inputValue().catch(() => "x"))) {
    await ta.fill(coverLetter).catch(() => {});
    log("dim", "   ↳ cover letter filled");
  }
}

/** Fill everything on the current step. Returns labels still missing. */
async function fillStep(root, ctx) {
  await uploadResume(root, ctx.resumePath);
  await fillCoverLetter(root, ctx.coverLetter);
  const a = await fillForm(root, ctx.profile, ctx.job);
  const b = await fillCustomSelects(root, ctx.profile, ctx.job);
  return [...a, ...b];
}

/** Generic multi-step form loop shared by all sites. */
async function runWizard(page, root, ctx, { next, submit, errors, maxSteps = 14 }) {
  let lastSig = "";
  let same = 0;
  for (let step = 0; step < maxSteps; step++) {
    await humanPause(1200, 2000);
    await dismissBanners(page);
    if (SUCCESS.test(await page.locator("body").innerText().catch(() => ""))) return { status: "applied", note: `Company site (${ctx.ats})` };
    if (await captchaPresent(page)) {
      const r = await handOver(page, ctx.job, ctx.mode, "there's a CAPTCHA to solve");
      if (r) return r;
    }
    const heading = ((await root.locator("h1, h2, h3").filter({ visible: true }).first().innerText({ timeout: 1000 }).catch(() => "")) || "").trim().split("\n")[0];
    log("dim", `   site step ${step + 1}${heading ? `: ${heading.slice(0, 70)}` : ""}`);

    const missing = await fillStep(root, ctx);
    if (missing.length) {
      const r = await handOver(page, ctx.job, ctx.mode, `please fill ${missing.slice(0, 4).map((f) => `"${f.label}"`).join(", ")}`);
      if (r) return r;
    }

    const sub = submit(root);
    if (await visible(sub)) {
      if (ctx.mode !== "auto" && !(await confirm(`Submit the application on ${ctx.job.company}'s site (${ctx.ats})? Check the Chrome tab first if you like.`))) {
        return { status: "skipped", note: "You chose not to submit on the company site" };
      }
      await sub.click().catch(() => {});
      await sleep(4000);
      const body = await page.locator("body").innerText().catch(() => "");
      if (SUCCESS.test(body)) return { status: "applied", note: `Company site (${ctx.ats})` };
      const err = errors(root);
      if (await visible(err)) {
        const msg = ((await err.innerText().catch(() => "")) || "").trim().split("\n")[0];
        const r = await handOver(page, ctx.job, ctx.mode, `the site says "${msg}"`);
        if (r) return r;
        continue;
      }
      // Some sites move to a "review" or extra page after the first submit; keep going.
      continue;
    }

    const nx = next(root);
    if (!(await visible(nx))) {
      const r = await handOver(page, ctx.job, ctx.mode, "I can't find a Next or Submit button");
      if (r) return r;
      continue;
    }
    await nx.click().catch(() => {});
    await sleep(2500);
    const err = errors(root);
    if (await visible(err)) {
      const msg = ((await err.innerText().catch(() => "")) || "").trim().split("\n")[0];
      log("warn", `   site says: ${msg}`);
      const again = await fillStep(root, ctx);
      if (!again.length && (await visible(nx))) {
        await nx.click().catch(() => {});
        await sleep(2500);
      }
      if (await visible(err)) {
        const r = await handOver(page, ctx.job, ctx.mode, `the site says "${msg}"`);
        if (r) return r;
      }
    }
    const sig = `${page.url()}|${heading}`;
    same = sig === lastSig ? same + 1 : 0;
    lastSig = sig;
    if (same >= 2) {
      same = 0;
      const r = await handOver(page, ctx.job, ctx.mode, "the form isn't moving to the next step");
      if (r) return r;
    }
  }
  return handOver(page, ctx.job, ctx.mode, "too many steps", false);
}

// ---------------------------------------------------------------- Workday
const wd = (root, id) => root.locator(`[data-automation-id="${id}"]`).filter({ visible: true }).first();

async function workdayAuth(page, ctx) {
  const email = ctx.profile.email;
  const password = process.env.ATS_PASSWORD || process.env.WORKDAY_PASSWORD;
  const onAuth = async () => (await visible(wd(page, "email"))) || (await visible(page.getByRole("button", { name: /^sign in$/i }).filter({ visible: true }).first()));
  if (!(await onAuth())) return null;
  if (!password) {
    return handOver(page, ctx.job, ctx.mode, "Workday needs you to sign in or create an account (add ATS_PASSWORD to .env to let me do it)");
  }
  // Try signing in first.
  if (!(await visible(wd(page, "email")))) await page.getByRole("button", { name: /^sign in$/i }).filter({ visible: true }).first().click().catch(() => {});
  await wd(page, "email").fill(email).catch(() => {});
  await wd(page, "password").fill(password).catch(() => {});
  await (await visible(wd(page, "signInSubmitButton")) ? wd(page, "signInSubmitButton") : btn(page, /^sign in$/i)).click().catch(() => {});
  await sleep(4000);
  if (!(await onAuth())) {
    log("dim", "   signed in to Workday");
    return null;
  }
  // No account on this company's Workday yet: create one.
  log("dim", "   creating a Workday account for this company");
  const create = (await visible(wd(page, "createAccountLink"))) ? wd(page, "createAccountLink") : btn(page, /create account/i);
  await create.click().catch(() => {});
  await sleep(2000);
  await wd(page, "email").fill(email).catch(() => {});
  await wd(page, "password").fill(password).catch(() => {});
  await wd(page, "verifyPassword").fill(password).catch(() => {});
  const agree = wd(page, "createAccountCheckbox");
  if (await visible(agree)) await agree.check({ force: true }).catch(() => agree.click().catch(() => {}));
  await ((await visible(wd(page, "createAccountSubmitButton"))) ? wd(page, "createAccountSubmitButton") : btn(page, /create account/i)).click().catch(() => {});
  await sleep(5000);
  const body = await page.locator("body").innerText().catch(() => "");
  if (/verify|verification|check your email|activate/i.test(body)) {
    const r = await handOver(page, ctx.job, ctx.mode, `Workday sent a verification email to ${email}. Click the link in that email, then sign in here`);
    if (r) return r;
  }
  if (await onAuth()) return handOver(page, ctx.job, ctx.mode, "I couldn't sign in or create the Workday account");
  return null;
}

async function workday(page, ctx) {
  // Job page → Apply → "Autofill with Resume" (lets Workday prefill experience) or "Apply Manually".
  const apply = (await visible(wd(page, "adventureButton"))) ? wd(page, "adventureButton") : btn(page, /^apply( now)?$/i);
  if (await visible(apply)) {
    await apply.click().catch(() => {});
    await sleep(2500);
  }
  const autofill = (await visible(wd(page, "autofillWithResume"))) ? wd(page, "autofillWithResume") : btn(page, /autofill with resume/i);
  const manual = (await visible(wd(page, "applyManually"))) ? wd(page, "applyManually") : btn(page, /apply manually/i);
  if (await visible(autofill)) await autofill.click().catch(() => {});
  else if (await visible(manual)) await manual.click().catch(() => {});
  await sleep(3000);

  const auth = await workdayAuth(page, ctx);
  if (auth) return auth;

  // "Autofill with Resume" page: upload, then continue.
  const root = page.locator("main, [role=main], body").first();
  return runWizard(page, root, ctx, {
    next: (r) => ((wd(r, "bottom-navigation-next-button"))),
    submit: (r) => wd(r, "bottom-navigation-next-button").filter({ hasText: /^submit$/i }),
    errors: (r) => r.locator("[data-automation-id=errorMessage], [data-automation-id=errorBanner], [role=alert]").filter({ visible: true }).filter({ hasText: /\S/ }).first(),
    maxSteps: 16,
  });
}

// ---------------------------------------------------------------- everything else
async function generic(page, ctx) {
  // Many career pages show the job first with an "Apply" button that reveals the form.
  const formVisible = async () => (await page.locator("form input:not([type=hidden]), form textarea").filter({ visible: true }).count().catch(() => 0)) > 2;
  if (!(await formVisible())) {
    const a = btn(page, /^(apply( now| for this job| to this job)?|i'?m interested)$/i);
    if (await visible(a)) {
      await a.click().catch(() => {});
      await sleep(3000);
    }
  }
  if (["icims", "oracle", "successfactors"].includes(ctx.ats) && (await page.locator("input[type=password]").filter({ visible: true }).count()) > 0) {
    const r = await handOver(page, ctx.job, ctx.mode, `${ctx.ats} wants you to sign in or create an account`);
    if (r) return r;
  }
  const root = page.locator("form").filter({ visible: true }).filter({ has: page.locator("input, textarea, select") }).first();
  const scope = (await visible(root)) ? root : page.locator("body");
  return runWizard(page, scope, ctx, {
    next: (r) => btn(r, /^(next|continue|save and continue|save & continue|proceed)$/i),
    submit: (r) => btn(r, /submit( application| your application)?$|send application|^apply( now)?$|complete application|finish/i),
    errors: (r) => r.locator("[role=alert], .error, .field-error, .error-message, [class*=error]:not(input)").filter({ visible: true }).filter({ hasText: /\S/ }).first(),
  });
}

/**
 * Apply on the company site. `open` clicks the job board's "Apply on company site" control
 * and returns the new tab (or the same page if it navigated).
 */
export async function applyExternal(page, job, { open, resumePath, profile, mode, coverLetter }) {
  let site;
  try {
    site = await open(page);
  } catch (e) {
    return { status: "needs_attention", note: `Couldn't open the company site: ${e.message.split("\n")[0]}` };
  }
  if (!site) return { status: "needs_attention", note: "Couldn't open the company site" };
  await site.waitForLoadState("load", { timeout: 20000 }).catch(() => {});
  await sleep(2000);
  const ats = detectAts(site.url());
  log("dim", `   company site: ${ats} · ${new URL(site.url()).hostname}`);
  const ctx = { job, resumePath, profile, mode, coverLetter, ats };
  let result;
  try {
    result = ats === "workday" ? await workday(site, ctx) : await generic(site, ctx);
  } catch (e) {
    result = await handOver(site, job, mode, `something went wrong (${e.message.split("\n")[0]})`, false);
  }
  if (site !== page) await site.close().catch(() => {});
  return result ?? { status: "needs_attention", note: "Company site: unfinished" };
}
