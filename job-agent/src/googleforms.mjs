// Google Forms applications (docs.google.com/forms, forms.gle). Questions are read from the
// form's own structure (listitem → heading + radios / checkboxes / dropdown / text / date /
// file upload), answered from her profile (Claude writes free-text answers), and the form is
// stepped through Next → Submit until "Your response has been recorded".
import { bestOption, quickAnswer } from "./forms.mjs";
import { answerQuestions } from "./llm.mjs";
import { confirm, humanPause, log, sleep } from "./util.mjs";

const DONE = /your response has been recorded|response recorded|thanks for (submitting|filling|your response)/i;

/** Reads every question on the current form page into a plain description. */
async function readQuestions(page) {
  return page.evaluate(() => {
    const clean = (s) => (s || "").replace(/\s+/g, " ").replace(/\*/g, "").trim();
    const out = [];
    document.querySelectorAll("[role=listitem]").forEach((item, i) => {
      const heading = item.querySelector("[role=heading]");
      if (!heading) return;
      item.setAttribute("data-gf", String(i));
      const label = clean(heading.innerText);
      const required = !!item.querySelector("[aria-label='Required question'], [aria-required=true]") || /\*/.test(heading.innerText);
      const radios = [...item.querySelectorAll("[role=radio]")];
      const checks = [...item.querySelectorAll("[role=checkbox]")];
      const listbox = item.querySelector("[role=listbox]");
      const text = item.querySelector("input[type=text], input[type=email], input[type=number], input[type=tel], input[type=url], input:not([type]), textarea");
      const date = item.querySelector("input[type=date]");
      const file = /add file|upload/i.test(item.innerText) && item.querySelector("[role=button]");
      const q = { idx: i, label, required };
      if (radios.length) Object.assign(q, { type: "radio", options: radios.map((r) => r.getAttribute("data-value") || r.getAttribute("aria-label") || ""), value: radios.find((r) => r.getAttribute("aria-checked") === "true")?.getAttribute("data-value") || "" });
      else if (checks.length) Object.assign(q, { type: "checkbox", options: checks.map((c) => c.getAttribute("data-answer-value") || c.getAttribute("aria-label") || ""), value: checks.filter((c) => c.getAttribute("aria-checked") === "true").length ? "x" : "" });
      else if (listbox) Object.assign(q, { type: "select", options: [...item.querySelectorAll("[role=option]")].map((o) => o.getAttribute("data-value") || o.innerText.trim()).filter((v) => v && !/^choose$/i.test(v)), value: clean(listbox.querySelector("[aria-selected=true]")?.getAttribute("data-value") || "").replace(/^choose$/i, "") });
      else if (date) Object.assign(q, { type: "date", value: date.value });
      else if (text) Object.assign(q, { type: text.tagName === "TEXTAREA" ? "textarea" : "text", value: text.value });
      else if (file) Object.assign(q, { type: "file", value: /\.pdf|\.docx?/i.test(item.innerText) ? "x" : "" });
      else return;
      out.push(q);
    });
    return out;
  });
}

async function fillQuestion(page, q, answer, resumePath) {
  const item = page.locator(`[data-gf="${q.idx}"]`);
  if (q.type === "radio") {
    const i = bestOption(q.options, answer);
    if (i < 0) {
      // "Other" option with a text box.
      const other = item.locator("[role=radio][data-value='__other_option__'], [role=radio][aria-label='Other:']").first();
      if (!(await other.count())) return false;
      await other.click();
      await item.locator("input[type=text]").last().fill(String(answer));
      return true;
    }
    await item.locator("[role=radio]").nth(i).click();
    return true;
  }
  if (q.type === "checkbox") {
    const wanted = String(answer).split(/\s*[,;|]\s*/).filter(Boolean);
    let n = 0;
    for (const w of wanted) {
      const i = bestOption(q.options, w);
      if (i >= 0) {
        await item.locator("[role=checkbox]").nth(i).click();
        n++;
      }
    }
    return n > 0;
  }
  if (q.type === "select") {
    const i = bestOption(q.options, answer);
    if (i < 0) return false;
    const lb = item.locator("[role=listbox]");
    const opt = page.locator(`[role=option][data-value="${q.options[i].replace(/"/g, '\\"')}"]`).filter({ visible: true }).last();
    await lb.click();
    if (!(await opt.isVisible({ timeout: 1500 }).catch(() => false))) {
      await lb.focus().catch(() => {});
      await page.keyboard.press("Space").catch(() => {});
    }
    await opt.click({ timeout: 4000 });
    await page.waitForTimeout(500);
    return true;
  }
  if (q.type === "date") {
    const d = new Date(answer);
    if (isNaN(d)) return false;
    await item.locator("input[type=date]").fill(d.toISOString().slice(0, 10));
    return true;
  }
  if (q.type === "file") return uploadToForm(page, item, resumePath);
  const box = item.locator("input[type=text], input[type=email], input[type=number], input[type=tel], input[type=url], input:not([type]), textarea").first();
  await box.fill(String(answer));
  return true;
}

/** Google Forms file questions open the Google Picker (needs Google sign-in). */
async function uploadToForm(page, item, resumePath) {
  if (!resumePath) return false;
  await item.getByRole("button", { name: /add file/i }).click().catch(() => {});
  for (let t = 0; t < 20; t++) {
    await sleep(700);
    const frame = page.frames().find((f) => /docs\.google\.com\/picker|picker/i.test(f.url()));
    if (!frame) continue;
    const input = frame.locator("input[type=file]").first();
    if (!(await input.count().catch(() => 0))) continue;
    await input.setInputFiles(resumePath);
    // The picker uploads, then either closes by itself or needs "Insert"/"Upload".
    for (let k = 0; k < 20; k++) {
      await sleep(1000);
      const done = await item.innerText().then((x) => /\.pdf/i.test(x)).catch(() => false);
      if (done) return true;
      await frame.getByRole("button", { name: /^(upload|insert|select)$/i }).click({ timeout: 500 }).catch(() => {});
    }
    return false;
  }
  return false;
}

/**
 * Fill and submit a Google Form. `handOver(reason)` asks the user (or marks needs-attention
 * in fully automatic mode); it returns null when the user fixed it and we should carry on.
 */
export async function googleForm(page, ctx, handOver) {
  const { profile, job, mode, resumePath } = ctx;
  for (let step = 0; step < 12; step++) {
    await page.waitForLoadState("load", { timeout: 15000 }).catch(() => {});
    await humanPause(1000, 1600);
    const body = await page.locator("body").innerText().catch(() => "");
    if (DONE.test(body)) return { status: "applied", note: "Google Form submitted" };
    if (/accounts\.google\.com/.test(page.url()) || /sign in to continue|you need permission|sign in to google/i.test(body)) {
      const r = await handOver("this Google Form needs you to be signed in to Google. Sign in once in the agent's Chrome");
      if (r) return r;
      continue;
    }

    const qs = await readQuestions(page);
    log("dim", `   form page ${step + 1}: ${qs.length} questions`);
    const empty = qs.filter((q) => !q.value);
    const quick = {};
    for (const q of empty) {
      if (q.type === "file") continue;
      const a = quickAnswer({ label: q.label, type: q.type === "textarea" ? "text" : q.type, options: q.options }, profile);
      if (a) quick[q.idx] = a;
    }
    const ask = empty.filter((q) => q.type !== "file" && !quick[q.idx]);
    let answers = {};
    if (ask.length) {
      try {
        answers = await answerQuestions(profile, job, ask.map((q) => ({
          key: `g${q.idx}`, label: q.label, required: q.required, options: q.options,
          type: q.type === "checkbox" ? "checkbox (several allowed: answer the matching options separated by commas)" : q.type,
        })));
      } catch (e) {
        log("warn", `   The AI couldn't answer (${e.message.split("\n")[0]})`);
      }
    }
    const missing = [];
    for (const q of empty) {
      const a = q.type === "file" ? "resume" : quick[q.idx] ?? answers[`g${q.idx}`];
      if (!a || a === "__ASK__") {
        if (q.required) missing.push(q.label);
        continue;
      }
      const ok = await fillQuestion(page, q, a, resumePath).catch(() => false);
      if (ok) log("dim", `   ↳ ${q.label.slice(0, 70)} → ${q.type === "file" ? "uploaded resume" : String(a).slice(0, 80)}`);
      else if (q.required) missing.push(q.label);
      await humanPause(150, 400);
    }
    if (missing.length) {
      const r = await handOver(`please answer ${missing.slice(0, 4).map((m) => `"${m}"`).join(", ")} in the form`);
      if (r) return r;
    }

    const submit = page.getByRole("button", { name: /^submit$/i }).filter({ visible: true }).first();
    const next = page.getByRole("button", { name: /^next$/i }).filter({ visible: true }).first();
    if (await submit.isVisible().catch(() => false)) {
      if (mode !== "auto" && !(await confirm(`Submit the Google Form for ${job.company} – ${job.title}?`))) return { status: "skipped", note: "You chose not to submit the Google Form" };
      await submit.click();
    } else if (await next.isVisible().catch(() => false)) {
      await next.click();
    } else {
      const r = await handOver("I can't find Next or Submit on this form");
      if (r) return r;
      continue;
    }
    await sleep(2500);
    const err = page.locator("[role=alert]").filter({ hasText: /required|must|valid|invalid/i }).filter({ visible: true }).first();
    if (await err.isVisible().catch(() => false)) {
      const r = await handOver(`the form says "${((await err.innerText().catch(() => "")) || "").trim().split("\n")[0]}"`);
      if (r) return r;
    }
  }
  return handOver("the form has too many pages");
}
