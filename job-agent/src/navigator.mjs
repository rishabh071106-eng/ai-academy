// The AI navigator: works through any web page the way a person would. Each step it
//  - looks at the page: a screenshot plus a numbered list of every button, link and field,
//    including ones inside embedded forms (iframes, e.g. Greenhouse/Lever widgets) and shadow DOM;
//  - asks the AI for ONE next action (click, type, choose an option, tick, upload the resume,
//    scroll, press a key, sign in…);
//  - does it, checks what changed, and remembers the outcome for the next step.
// Used for company career sites, stuck application dialogs, Google Forms and Alignerr.
import { generateJSON } from "./ai.mjs";
import { bestOption, fillCustomSelects, fillForm } from "./forms.mjs";
import { ask, askForHelp, confirm, loadConfig, log, sleep, stopIfFatalApiError } from "./util.mjs";

const PASSWORD_TOKEN = "{{PASSWORD}}";
const password = () => process.env.ATS_PASSWORD || process.env.WORKDAY_PASSWORD || "";

// Runs inside each frame: numbers the interactive elements and returns them with page text.
function tagFrame(prefix) {
  const clean = (s) => (s || "").replace(/\s+/g, " ").trim();
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const st = getComputedStyle(el);
    return r.width > 1 && r.height > 1 && st.visibility !== "hidden" && st.display !== "none" && Number(st.opacity) > 0.05;
  };
  const deepAll = (node, sel) => {
    const out = [...node.querySelectorAll(sel)];
    for (const el of node.querySelectorAll("*")) if (el.shadowRoot) out.push(...deepAll(el.shadowRoot, sel));
    return out;
  };
  for (const e of deepAll(document, "[data-ja-ui]")) e.removeAttribute("data-ja-ui");
  const sel =
    "a[href], button, [role=button], [role=link], [role=tab], [role=menuitem], [role=option], [role=checkbox], [role=radio], [role=switch], [role=combobox], [role=listbox], input:not([type=hidden]), select, textarea, [contenteditable=true], label[for], [tabindex='0'][class*=upload i], [class*=dropzone i]";
  // The question a field belongs to, when it has no proper label.
  const question = (el) => {
    const by = el.getAttribute("aria-labelledby");
    if (by) {
      const t = by.split(/\s+/).map((id) => document.getElementById(id)?.innerText || "").join(" ");
      if (clean(t)) return clean(t);
    }
    if (el.labels?.[0]) return clean(el.labels[0].innerText);
    let box = el.parentElement;
    for (let i = 0; i < 5 && box; i++, box = box.parentElement) {
      const t = clean(box.innerText);
      if (t && t.length > 3 && t.length < 260) return t;
    }
    return "";
  };
  const els = [];
  let n = 0;
  const vh = innerHeight;
  for (const el of deepAll(document, sel)) {
    if (n >= 180) break;
    const isFile = el.matches("input[type=file]");
    if (!isFile && !visible(el)) continue;
    // Radios/checkboxes are often visually hidden behind a styled label: keep them if the label is visible.
    const id = `${prefix}${n++}`;
    el.setAttribute("data-ja-ui", id);
    const tag = el.tagName.toLowerCase();
    const r = el.getBoundingClientRect();
    const label = el.getAttribute("aria-label") || el.getAttribute("placeholder") || el.getAttribute("title") || "";
    const isField = /input|select|textarea/.test(tag) || el.isContentEditable || /combobox|checkbox|radio|switch|listbox/.test(el.getAttribute("role") || "");
    els.push({
      id,
      tag,
      role: el.getAttribute("role") || "",
      type: el.getAttribute("type") || "",
      text: clean(tag === "select" ? "" : el.innerText || (tag === "input" && /submit|button/.test(el.type) ? el.value : "")).slice(0, 110),
      label: clean(label).slice(0, 110),
      question: isField ? question(el).slice(0, 200) : "",
      value: tag === "select" ? clean(el.selectedOptions?.[0]?.text) : /input|textarea/.test(tag) && el.type !== "file" ? (el.type === "password" ? (el.value ? "••••" : "") : clean(el.value).slice(0, 60)) : "",
      options: tag === "select" ? [...el.options].map((o) => clean(o.text)).filter(Boolean).slice(0, 25) : undefined,
      files: isFile ? [...(el.files || [])].map((f) => f.name).join(", ") || "none" : undefined,
      accept: isFile ? el.getAttribute("accept") || "" : undefined,
      checked: el.checked || el.getAttribute("aria-checked") === "true" || undefined,
      required: el.required || el.getAttribute("aria-required") === "true" || undefined,
      invalid: el.getAttribute("aria-invalid") === "true" || undefined,
      href: tag === "a" ? (el.getAttribute("href") || "").slice(0, 100) : undefined,
      disabled: el.disabled || el.getAttribute("aria-disabled") === "true" || undefined,
      offscreen: !isFile && (r.bottom < 0 || r.top > vh) ? (r.top > vh ? "below" : "above") : undefined,
    });
  }
  const headings = deepAll(document, "h1, h2, h3, [role=heading], legend").filter(visible).map((h) => clean(h.innerText)).filter(Boolean).slice(0, 30);
  const errors = deepAll(document, "[role=alert], [aria-live=assertive], .error, .error-message, .field-error, [class*=error-text], [class*=errorMessage], [id*=error]")
    .filter(visible)
    .map((e) => clean(e.innerText))
    .filter((t) => t && t.length < 200)
    .slice(0, 10);
  const dialogs = deepAll(document, "[role=dialog], [role=alertdialog], [aria-modal=true]").filter(visible).map((d) => clean(d.innerText).slice(0, 1500));
  const body = clean(document.body?.innerText || "");
  return { url: location.href, title: document.title, headings, errors, dialogs, text: body.slice(0, 6000), elements: els, scroll: { y: Math.round(scrollY), max: Math.round(document.documentElement.scrollHeight - innerHeight) } };
}

/** Snapshot of the page and its visible iframes. */
export async function snapshot(page) {
  const frames = [];
  for (const f of page.frames()) {
    if (frames.length >= 6) break;
    if (f !== page.mainFrame()) {
      if (/recaptcha|hcaptcha|challenges\.cloudflare|doubleclick|googletagmanager|facebook\.com\/tr|about:blank/.test(f.url()) || !f.url()) continue;
      const box = await (await f.frameElement().catch(() => null))?.boundingBox().catch(() => null);
      if (!box || box.width < 120 || box.height < 80) continue;
    }
    frames.push(f);
  }
  const parts = await Promise.all(frames.map((f, i) => f.evaluate(tagFrame, i === 0 ? "e" : `f${i}e`).catch(() => null)));
  const main = parts[0];
  if (!main) return null;
  const elements = [];
  const frameOf = new Map();
  parts.forEach((p, i) => p?.elements.forEach((e) => {
    if (i > 0) e.frame = new URL(p.url).hostname;
    elements.push(e);
    frameOf.set(e.id, frames[i]);
  }));
  const extra = parts.slice(1).filter(Boolean).map((p) => `[embedded form from ${new URL(p.url).hostname}] ${p.headings.join(" | ")} ${p.text.slice(0, 2500)}`);
  return {
    url: main.url,
    title: main.title,
    headings: [...main.headings, ...parts.slice(1).flatMap((p) => p?.headings ?? [])].slice(0, 40),
    errors: parts.flatMap((p) => p?.errors ?? []).slice(0, 12),
    dialogs: main.dialogs,
    text: [main.dialogs.join(" | "), main.text, ...extra].filter(Boolean).join("\n").slice(0, 9000),
    scroll: main.scroll,
    elements: elements.slice(0, 260),
    frameOf,
  };
}

const obj = (properties) => ({ type: "object", properties, required: Object.keys(properties), additionalProperties: false });
const str = { type: "string" };
const STEP_SCHEMA = obj({
  observation: { type: "string", description: "What the page shows right now, in one sentence (which step of the application, any errors)" },
  reasoning: { type: "string", description: "Why this action is the best next step" },
  action: { type: "string", enum: ["click", "type", "choose", "check", "upload_resume", "fill_form", "press", "scroll", "wait", "back", "goto", "report_jobs", "done", "need_user"] },
  target: { type: "string", description: "Element id like e12 or f1e4, or empty" },
  value: { type: "string", description: "type: the text · choose: the option to pick · press: a key like Enter/Tab/ArrowDown/Escape · scroll: down/up · goto: URL · otherwise empty" },
  jobs: { type: "array", description: "Only for report_jobs: every role on the page", items: obj({ title: str, target: str, href: str, summary: str, already_applied: { type: "boolean" } }) },
  status: { type: "string", enum: ["applied", "already_applied", "not_eligible", "needs_user", "none"] },
  message: { type: "string", description: "For done / need_user: what happened, or exactly what the person must do" },
});

function herData(profile) {
  const { applicationAnswers = {}, experience = [], education = [], ...p } = profile;
  const [first, ...rest] = String(p.name || "").split(" ");
  return JSON.stringify(
    {
      name: p.name, firstName: first, lastName: rest.join(" "), email: p.email, phone: p.phone, phoneCountryCode: p.phoneCountryCode || "+91",
      city: p.city, address: p.address, country: "India", linkedin: p.linkedinUrl, headline: p.headline, totalExperienceYears: p.totalExperienceYears,
      skills: p.skills, skillYears: p.skillYears,
      experience: experience.map((e) => ({ company: e.company, role: e.role, location: e.location, start: e.start, end: e.end, client: e.client })),
      education: education.map((e) => ({ degree: e.degree, field: e.field, institution: e.institution, start: e.start, end: e.end, year: e.year, status: e.status })),
      answers: applicationAnswers,
    },
    null,
    0,
  ).slice(0, 7000);
}

async function decide({ goal, rules, snap, shot, history, profile, job }) {
  const hasPassword = !!password();
  const elements = snap.elements
    .map((e) => {
      const bits = [`${e.id} ${e.tag}${e.role ? `[${e.role}]` : ""}${e.type ? `(${e.type})` : ""}`];
      if (e.text) bits.push(`"${e.text}"`);
      if (e.label && e.label !== e.text) bits.push(`label="${e.label}"`);
      if (e.question && e.question !== e.label && e.question !== e.text) bits.push(`q="${e.question}"`);
      if (e.value) bits.push(`value="${e.value}"`);
      if (e.options) bits.push(`options=[${e.options.join(" / ")}]`);
      if (e.files) bits.push(`files=${e.files}${e.accept ? ` accept=${e.accept}` : ""}`);
      for (const k of ["checked", "required", "invalid", "disabled"]) if (e[k]) bits.push(k);
      if (e.offscreen) bits.push(`(${e.offscreen} the visible area)`);
      if (e.href) bits.push(`href=${e.href}`);
      if (e.frame) bits.push(`[in ${e.frame}]`);
      return bits.join(" ");
    })
    .join("\n");
  const content = [
    {
      type: "text",
      text: `GOAL: ${goal}
${job ? `ROLE: ${job.title}${job.company ? ` at ${job.company}` : ""}\nJOB POST (excerpt): ${String(job.description || "").replace(/\s+/g, " ").slice(0, 1500)}` : ""}

HER DATA:
${herData(profile)}
Password for job-site accounts: ${hasPassword ? `available — type the literal text ${PASSWORD_TOKEN} into password fields (also "confirm password")` : "NOT available"}.
Her tailored resume PDF is ready for upload_resume.

WHAT YOU DID SO FAR (oldest first):
${history.slice(-14).map((h, i) => `${i + 1}. ${h}`).join("\n") || "(nothing yet)"}

PAGE: ${snap.title} — ${snap.url}
Scroll: ${snap.scroll.y}px of ${snap.scroll.max}px
Headings: ${snap.headings.join(" | ")}
${snap.errors.length ? `ERROR MESSAGES ON PAGE: ${snap.errors.join(" | ")}\n` : ""}Text: ${snap.text.slice(0, 7000)}

ELEMENTS (ids for target):
${elements}

The screenshot shows the visible part of the page.`,
    },
  ];
  if (shot) content.push({ type: "image", source: { type: "base64", media_type: "image/jpeg", data: shot } });
  return generateJSON({
    role: "navigator",
    effort: "medium",
    maxTokens: 8000,
    schema: STEP_SCHEMA,
    system: `You are applying for jobs on behalf of Aishwarya Sharma, operating a real Chrome browser exactly like a careful human assistant would. You see a screenshot and a numbered list of the page's elements. Choose exactly ONE next action.

Actions:
- click(target) — buttons, links, tabs, "Apply", "Next", "Continue", "Submit", menu items, options in an open dropdown.
- type(target, value) — text fields. For autocomplete fields (city, school, company…) type, then click the matching suggestion in the next step.
- choose(target, value) — pick an option in a <select> or custom dropdown/combobox; value is the option text you want.
- check(target) — tick a checkbox / radio / switch (consent boxes, "Yes"/"No" radios).
- upload_resume(target) — attach her resume: target the file input, the "Upload"/"Attach"/"Choose file" button or the drop zone. Use it whenever a resume/CV is asked for and files=none.
- fill_form — fills every empty standard field on the page from her data at once (name, email, phone, links, experience…). Good first move on a new form page; then fix whatever is still empty or flagged.
- press(value) — a key: Enter, Tab, Escape, ArrowDown…
- scroll(value "down"/"up", or target to bring an element into view) — forms are long; scroll to find required fields and the Next/Submit button below.
- wait — the page is loading or processing an upload.
- back · goto(value=url) · report_jobs(jobs) · done(status, message) · need_user(message).

How to work:
- Think like a person filling the application: read the screenshot and the error messages, fill every required field (marked *, required or invalid), then press Next/Continue/Submit. After submitting, look for the confirmation.
- Answer screening questions truthfully from HER DATA; write short, natural answers for open questions ("why this role", "cover letter") using the job post and her experience (Magento/Adobe Commerce, PHP, React/Next.js, 9+ years). Salary in INR as in her answers. Notice period from her answers.
- To apply, many career sites need an account: sign in or create one with her email and the password token; tick the terms box needed to register.
- If an "Apply" button opens a new tab or a different site (Workday, Greenhouse, Lever, iCIMS, Taleo, SuccessFactors, Zoho, Freshteam, Keka, Darwinbox…), keep going there.
- If the page is only a company homepage or job list, find the matching job (search for the role title) and its Apply button.
- When the same action did not change anything, don't repeat it: scroll, look for an error message, pick another element, or try another way.
- Use done(status "applied") ONLY when the page clearly confirms the application was submitted (or says she already applied → "already_applied"). Use done(status "not_eligible") when there's no way to apply (job closed, no application form, location not allowed).
- need_user ONLY for things a person must do: CAPTCHA / "I'm not a robot", an email or SMS verification code, a password reset, a skill test, a video/AI interview, payment, or data she has never given (e.g. PAN, date of birth if not in her data).
- Never invent facts; never pay; never change account security settings; never delete anything; never log out.
- Close cookie banners and pop-ups that block the page.
${rules || ""}`,
    content,
  });
}

const findEl = (page, snap, id) => (snap.frameOf.get(id) ?? page.mainFrame()).locator(`[data-ja-ui="${id}"]`).first();
const fill = (v) => String(v ?? "").replaceAll(PASSWORD_TOKEN, password());

/** Pick `value` in a native select or a custom dropdown. */
async function choose(page, loc, value) {
  const tag = await loc.evaluate((x) => x.tagName).catch(() => "");
  if (tag === "SELECT") {
    const opts = await loc.evaluate((x) => [...x.options].map((o) => o.text.trim()));
    const i = bestOption(opts, value);
    if (i < 0) throw new Error(`no option like "${value}" (options: ${opts.slice(0, 8).join(" / ")})`);
    await loc.selectOption({ index: i });
    return opts[i];
  }
  await loc.click({ timeout: 5000 });
  await sleep(500);
  // Searchable dropdowns: type to filter.
  if (await loc.evaluate((x) => x.tagName === "INPUT" || x.isContentEditable).catch(() => false)) {
    await loc.fill("").catch(() => {});
    await loc.pressSequentially(String(value).slice(0, 40), { delay: 40 }).catch(() => {});
    await sleep(1200);
  }
  for (const frame of page.frames()) {
    const opts = frame.locator("[role=option], [role=menuitem], [role=listbox] li, li[class*=option i], div[class*=option i]:not(:has(div[class*=option i])), [data-automation-id=promptOption]").filter({ visible: true });
    const texts = (await opts.allInnerTexts().catch(() => [])).map((t) => t.trim());
    if (!texts.length) continue;
    const i = bestOption(texts, value);
    if (i >= 0) {
      await opts.nth(i).click({ timeout: 4000 });
      return texts[i];
    }
  }
  await page.keyboard.press("Enter").catch(() => {});
  return `${value} (pressed Enter)`;
}

/** Attach the resume through a file input, an upload button, a menu or a drop zone. */
async function upload(page, loc, resumePath) {
  const isInput = await loc.evaluate((x) => x.tagName === "INPUT" && x.type === "file").catch(() => false);
  if (isInput) {
    await loc.setInputFiles(resumePath);
    return "file input";
  }
  // A file input hidden next to the button / inside the drop zone.
  const near = await loc.evaluateHandle((x) => {
    let box = x;
    for (let i = 0; i < 5 && box; i++, box = box.parentElement) {
      const f = box.querySelector?.("input[type=file]");
      if (f) return f;
    }
    return null;
  }).catch(() => null);
  if (near && (await near.evaluate((x) => !!x).catch(() => false))) {
    await near.asElement().setInputFiles(resumePath);
    return "file input next to the button";
  }
  // Click it like a person and answer the file chooser; some buttons open a small menu first.
  const chooser = page.waitForEvent("filechooser", { timeout: 7000 }).catch(() => null);
  await loc.click({ timeout: 5000 });
  let fc = await chooser;
  if (!fc) {
    const local = page.getByRole("button", { name: /upload|from (my )?(computer|device)|local|browse|attach|choose file/i }).or(page.getByRole("menuitem", { name: /upload|computer|device|local|browse/i })).filter({ visible: true }).first();
    if (await local.isVisible().catch(() => false)) {
      const again = page.waitForEvent("filechooser", { timeout: 7000 }).catch(() => null);
      await local.click({ timeout: 4000 }).catch(() => {});
      fc = await again;
    }
  }
  if (fc) {
    await fc.setFiles(resumePath);
    return "file picker";
  }
  // Last resort: any resume/CV file input on the page (or in an embedded form).
  for (const frame of page.frames()) {
    const inputs = frame.locator("input[type=file]");
    if ((await inputs.count().catch(() => 0)) > 0) {
      await inputs.first().setInputFiles(resumePath);
      return "page's file input";
    }
  }
  throw new Error("no file input or file picker appeared");
}

/** URL + headings + amount of text: enough to tell whether an action did something. */
const pageSig = (page) =>
  page.evaluate(() => `${location.href}|${[...document.querySelectorAll("h1,h2,h3,legend,[role=alert]")].slice(0, 8).map((h) => h.innerText.trim()).join("|")}|${Math.round((document.body?.innerText.length || 0) / 50)}`).catch(() => "");

async function screenshot(page) {
  return page.screenshot({ type: "jpeg", quality: 55, timeout: 8000 }).then((b) => b.toString("base64")).catch(() => null);
}

/**
 * Work towards `goal` on the current page. Returns { status, note, jobs? }.
 * opts: { goal, rules, profile, job, resumePath, mode, maxSteps, stopOnReport }
 */
export async function navigate(page, opts) {
  const { goal, profile, job, resumePath, mode = "review", stopOnReport = false } = opts;
  const maxSteps = opts.maxSteps ?? Number(loadConfig().navigatorMaxSteps ?? 45);
  const history = opts.history ?? [];
  const lastActions = [];
  let reported = [];
  for (let step = 0; step < maxSteps; step++) {
    await page.waitForLoadState("domcontentloaded").catch(() => {});
    await sleep(1000);
    const snap = await snapshot(page).catch(() => null);
    if (!snap) {
      await sleep(1500);
      continue;
    }
    const shot = loadConfig().navigatorScreenshots === false ? null : await screenshot(page);
    let d;
    try {
      d = await decide({ goal, rules: opts.rules, snap, shot, history, profile, job });
    } catch (e) {
      stopIfFatalApiError(e);
      log("warn", `   navigator: ${e.message.split("\n")[0]}`);
      return { status: "needs_attention", note: `Couldn't decide the next step (${e.message.split("\n")[0]})` };
    }
    const t = d.target ? snap.elements.find((x) => x.id === d.target) : null;
    const tName = t ? ` "${(t.text || t.label || t.question || t.tag).slice(0, 50)}"` : "";
    const shown = d.action === "type" && /password/i.test(`${t?.type} ${t?.label}`) ? "••••" : (d.value || "").slice(0, 50);
    const desc = `${d.action}${tName}${shown ? ` = ${shown}` : ""}`;
    log("dim", `   → ${desc}  (${(d.reasoning || "").slice(0, 100)})`);

    // Same action three times in a row without progress: say so, so the model changes approach.
    lastActions.push(desc);
    const repeated = lastActions.slice(-3).length === 3 && new Set(lastActions.slice(-3)).size === 1;

    const before = await pageSig(page);
    let outcome = "";
    try {
      const loc = d.target ? findEl(page, snap, d.target) : null;
      if (["click", "type", "choose", "check", "upload_resume"].includes(d.action) && d.action !== "upload_resume" && !loc) throw new Error("no target given");
      if (loc) await loc.scrollIntoViewIfNeeded({ timeout: 3000 }).catch(() => {});
      switch (d.action) {
        case "click": {
          const label = `${t?.text || ""} ${t?.label || ""}`;
          if (mode !== "auto" && /submit|send application|finish|complete application/i.test(label)) {
            if (!(await confirm(`Submit the application${job ? ` for ${job.title}` : ""}?`))) return { status: "skipped", note: "You chose not to submit" };
          }
          const popup = page.context().waitForEvent("page", { timeout: 3000 }).catch(() => null);
          await loc.click({ timeout: 6000 }).catch(async (e) => {
            // Covered by an overlay or styled away: click it from inside the page.
            if (!/intercept|not visible|outside of the viewport|timeout/i.test(e.message)) throw e;
            await loc.evaluate((x) => x.click());
          });
          const tab = await popup;
          if (tab) {
            log("dim", "   (opened in a new tab; continuing there)");
            await tab.waitForLoadState("domcontentloaded").catch(() => {});
            history.push(`${desc} → opened a new tab`);
            return navigate(tab, { ...opts, history, maxSteps: maxSteps - step - 1 });
          }
          break;
        }
        case "type": {
          const value = fill(d.value);
          await loc.fill(value, { timeout: 5000 }).catch(async () => {
            await loc.click({ timeout: 4000 });
            await page.keyboard.press(process.platform === "darwin" ? "Meta+A" : "Control+A");
            await page.keyboard.type(value, { delay: 25 });
          });
          // Autocomplete fields show suggestions; tell the model on the next step.
          await sleep(900);
          break;
        }
        case "choose":
          outcome = `picked "${await choose(page, loc, fill(d.value))}"`;
          break;
        case "check": {
          const ok = await loc.check({ timeout: 4000 }).then(() => true).catch(() => false);
          if (!ok) await loc.click({ timeout: 4000 }).catch(() => loc.evaluate((x) => x.click()));
          break;
        }
        case "upload_resume": {
          if (!resumePath) {
            outcome = "no resume file available";
            break;
          }
          const how = await upload(page, loc ?? page.locator("input[type=file]").first(), resumePath);
          log("dim", `   ↳ uploaded tailored resume (${how})`);
          await sleep(3500); // sites parse the resume and prefill fields
          outcome = `uploaded via ${how}`;
          break;
        }
        case "fill_form": {
          const missing = [];
          for (const frame of [...new Set(snap.frameOf.values())]) {
            const root = frame.locator("body");
            missing.push(...(await fillForm(root, profile, job || {}).catch(() => [])), ...(await fillCustomSelects(root, profile, job || {}).catch(() => [])));
          }
          outcome = missing.length ? `left empty: ${missing.map((m) => m.label).join("; ").slice(0, 300)}` : "filled";
          break;
        }
        case "press":
          await page.keyboard.press(d.value || "Enter");
          break;
        case "scroll":
          if (loc) break; // scrolled into view above
          await page.mouse.move(640, 400).catch(() => {});
          await page.mouse.wheel(0, /up/i.test(d.value) ? -900 : 900);
          await sleep(600);
          break;
        case "wait":
          await sleep(3500);
          break;
        case "back":
          await page.goBack({ waitUntil: "domcontentloaded" }).catch(() => {});
          break;
        case "goto":
          await page.goto(d.value, { waitUntil: "domcontentloaded" });
          break;
        case "report_jobs":
          reported = d.jobs || [];
          if (stopOnReport) return { status: "none", note: "", jobs: reported };
          break;
        case "done":
          return {
            status: d.status === "applied" || d.status === "already_applied" ? "applied" : d.status === "not_eligible" ? "skipped" : "needs_attention",
            note: d.message || d.status,
            jobs: reported,
          };
        case "need_user": {
          await page.bringToFront().catch(() => {});
          const choices = [
            { label: "Done, continue", value: "" },
            { label: "It's applied", value: "done" },
            { label: "Skip", value: "s" },
          ];
          const q = `${job ? `${job.title} at ${job.company}: ` : ""}${d.message}`;
          const r = mode === "auto" ? await askForHelp(q, choices) : await ask(q, choices);
          if (r === null || r === "s") return { status: "needs_attention", note: d.message };
          if (r === "done") return { status: "applied", note: "Finished by you" };
          history.push(`need_user: ${d.message} → the person did it; continue`);
          continue;
        }
      }
    } catch (e) {
      outcome = `FAILED: ${e.message.split("\n")[0].slice(0, 140)}`;
    }
    await sleep(700);
    const changed = (await pageSig(page)) !== before ? "page changed" : "no visible change";
    history.push(`${desc}${outcome ? ` → ${outcome}` : ""}${["type", "fill_form", "choose", "check"].includes(d.action) && !outcome.startsWith("FAILED") ? "" : ` → ${changed}`}${repeated ? " → WARNING: same action 3 times; it is not working, do something different" : ""}`);
  }
  return { status: "needs_attention", note: "Ran out of steps", jobs: reported };
}
