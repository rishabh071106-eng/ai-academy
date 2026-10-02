// Generic form reading/filling for application modals (LinkedIn Easy Apply, Naukri questionnaires).
import { answerQuestions } from "./llm.mjs";
import { humanPause, log } from "./util.mjs";

/**
 * Reads every visible, fillable field inside `root` and tags it with data-ja-key.
 * Returns [{ key, label, type, required, value, options? }].
 */
export async function collectFields(root) {
  return root.evaluate((rootEl) => {
    // querySelectorAll that also looks inside shadow roots (LinkedIn renders parts of the form in web components).
    const deepAll = (node, sel) => {
      const out = [...node.querySelectorAll(sel)];
      for (const el of node.querySelectorAll("*")) if (el.shadowRoot) out.push(...deepAll(el.shadowRoot, sel));
      return out;
    };
    const byId = (el, id) => el.getRootNode()?.getElementById?.(id) || document.getElementById(id);
    const visible = (el) => !!(el && (el.offsetParent || el.getClientRects().length));
    const clean = (s) => (s || "").replace(/\s+/g, " ").replace(/\*/g, "").trim();
    const labelOf = (el) => {
      if (el.labels && el.labels[0]) return clean(el.labels[0].innerText);
      const by = el.getAttribute("aria-labelledby");
      if (by) return clean(by.split(" ").map((id) => byId(el, id)?.innerText || "").join(" "));
      if (el.getAttribute("aria-label")) return clean(el.getAttribute("aria-label"));
      const fs = el.closest("fieldset");
      if (fs && fs.querySelector("legend")) return clean(fs.querySelector("legend").innerText);
      const wrap = el.closest("[class*=form-element], [class*=formElement], .form-group, div");
      const lab = wrap && wrap.querySelector("label, [class*=label]");
      return clean(lab?.innerText || el.placeholder || el.name || "");
    };
    const fields = [];
    let n = 0;
    const seenRadio = new Set();
    for (const el of deepAll(rootEl, "input, select, textarea")) {
      const type = (el.tagName === "INPUT" ? el.type || "text" : el.tagName).toLowerCase();
      if (["hidden", "submit", "button", "file", "search", "image", "reset"].includes(type)) continue;
      if (el.getAttribute("role") === "combobox" || el.closest("[role=combobox], [data-automation-id=multiselectInputContainer]")) continue; // custom dropdowns: fillCustomSelects
      if (el.disabled || el.readOnly) continue;
      if (type === "radio") {
        const name = el.name || el.id;
        if (seenRadio.has(name)) continue;
        seenRadio.add(name);
        const group = deepAll(el.getRootNode(), `input[type=radio][name="${CSS.escape(name)}"]`);
        if (!group.some((r) => visible(r) || visible(r.labels?.[0]))) continue;
        const fs = el.closest("fieldset");
        const key = `ja${n++}`;
        group.forEach((r) => r.setAttribute("data-ja-key", key));
        fields.push({
          key, type: "radio",
          label: clean(fs?.querySelector("legend")?.innerText || fs?.querySelector("span, label")?.innerText || name),
          required: group.some((r) => r.required) || !!fs?.querySelector("[class*=required]") || /\*/.test(fs?.innerText || ""),
          options: group.map((r) => clean(r.labels?.[0]?.innerText || r.value)),
          value: clean(group.find((r) => r.checked)?.labels?.[0]?.innerText || ""),
        });
        continue;
      }
      if (!visible(el)) continue;
      const key = `ja${n++}`;
      el.setAttribute("data-ja-key", key);
      const f = { key, type, label: labelOf(el), required: el.required || el.getAttribute("aria-required") === "true" };
      if (type === "select") {
        f.options = [...el.options].map((o) => clean(o.text)).filter((t) => t && !/^select/i.test(t));
        const sel = el.options[el.selectedIndex];
        f.value = sel && !/^select/i.test(sel.text) && sel.value !== "" ? clean(sel.text) : "";
      } else if (type === "checkbox") {
        f.value = el.checked ? "Yes" : "";
      } else {
        f.value = el.value;
      }
      fields.push(f);
    }
    return fields;
  });
}

/** Answers that come straight from the profile, no LLM needed. */
export function quickAnswer(field, profile) {
  const l = field.label.toLowerCase();
  const [first, ...rest] = profile.name.split(" ");
  if (/e-?mail/.test(l)) return profile.email;
  if (/country (phone |dial(ing)? )?code|phone (country )?code|dial(ing)? code/.test(l) && !/(number|mobile).*country code/.test(l)) return field.options?.length ? field.options.find((o) => /india|\+91/i.test(o)) ?? null : profile.phoneCountryCode || "+91";
  const cc = profile.phoneCountryCode || "+91";
  const digits = String(profile.phone).replace(/\D/g, "").replace(/^91(?=\d{10}$)/, "");
  if (/(mobile|phone).*(with|incl\w*).*(country|code)|international|e\.?164/.test(l)) return `${cc} ${digits}`;
  if (/whatsapp|mobile|phone|contact number/.test(l)) return digits;
  if (/^(country|country of residence)$/.test(l)) return field.options?.find((o) => /india/i.test(o)) ?? "India";
  if (/first name|given name/.test(l)) return first;
  if (/last name|surname|family name/.test(l)) return rest.join(" ");
  if (/^(full )?name$/.test(l)) return profile.name;
  if (/linkedin/.test(l) && profile.linkedinUrl) return profile.linkedinUrl;
  if (/^(location|city|current city|location \(city\))$/.test(l)) return profile.city;
  if (/total (years of )?(work )?experience|overall experience/.test(l) && field.type !== "select") return String(profile.totalExperienceYears);
  const a = profile.applicationAnswers ?? {};
  if (/preferred (first )?name/.test(l)) return first;
  if (/^(signature|full legal name|legal name|your name)/.test(l)) return profile.name;
  if (/current (company|employer)/.test(l) && a.currentCompany) return a.currentCompany;
  if (/current (job )?title|current (role|designation)/.test(l) && a.currentTitle) return a.currentTitle;
  if (/how did you (hear|find|learn)|source of (application|referral)/.test(l)) return field.options?.find((o) => /linkedin/i.test(o)) ?? field.options?.find((o) => /job board|website|online/i.test(o)) ?? (field.options?.length ? null : "LinkedIn");
  // Consent / acknowledgement checkboxes on application forms.
  if (field.type === "checkbox" && /agree|terms|consent|acknowledg|certify|privacy|confirm that|i understand/.test(l)) return "Yes";
  return null;
}

async function fillOne(root, field, answer) {
  const el = root.locator(`[data-ja-key="${field.key}"]`);
  const page = root.page();
  if (field.type === "radio") {
    const idx = bestOption(field.options, answer);
    if (idx < 0) return false;
    const radio = el.nth(idx);
    const id = await radio.getAttribute("id");
    const label = id ? root.locator(`label[for="${id}"]`) : null;
    if (label && (await label.count())) await label.first().click();
    else await radio.check({ force: true });
    return true;
  }
  if (field.type === "select") {
    const idx = bestOption(field.options, answer);
    if (idx < 0) return false;
    await el.first().selectOption({ label: field.options[idx] }).catch(async () => {
      // Option text was cleaned; fall back to matching the raw <option> by index among non-placeholder options.
      const values = await el.first().evaluate((s) => [...s.options].filter((o) => o.value && !/^select/i.test(o.text)).map((o) => o.value));
      await el.first().selectOption(values[idx]);
    });
    return true;
  }
  if (field.type === "checkbox") {
    if (/^(yes|true|agree|i agree)/i.test(answer)) await el.first().check({ force: true });
    return true;
  }
  await el.first().click({ timeout: 2000 }).catch(() => {});
  await el.first().fill("");
  await el.first().pressSequentially(String(answer), { delay: 25 });
  // React-controlled inputs sometimes drop typed text; check and retry once with a plain fill.
  if (!(await el.first().inputValue().catch(() => "")).trim()) await el.first().fill(String(answer)).catch(() => {});
  // Typeahead fields (e.g. city) show a suggestion list; pick the first suggestion.
  const option = page.locator("[role=listbox] [role=option], .basic-typeahead__selectable, .search-typeahead-v2__hit").first();
  if (await option.isVisible({ timeout: 1200 }).catch(() => false)) await option.click();
  return true;
}

export function bestOption(options = [], answer) {
  const a = String(answer).trim().toLowerCase();
  // A number against range options ("0-3 years", "4-7", "8+ years", "more than 10").
  const num = /^\d+(\.\d+)?$/.test(a) ? Number(a) : null;
  if (num !== null && !options.some((o) => o.trim().toLowerCase() === a)) {
    const hit = options.findIndex((o) => {
      const t = o.toLowerCase();
      const r = t.match(/(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)/);
      if (r) return num >= +r[1] && num <= +r[2];
      const plus = t.match(/(\d+(?:\.\d+)?)\s*\+|(?:more than|above|over|greater than)\s*(\d+(?:\.\d+)?)/);
      if (plus) return num >= +(plus[1] ?? plus[2]);
      const less = t.match(/(?:less than|below|under|upto|up to)\s*(\d+(?:\.\d+)?)/);
      if (less) return num < +less[1];
      return false;
    });
    if (hit >= 0) return hit;
  }
  let i = options.findIndex((o) => o.toLowerCase() === a);
  if (i < 0) i = options.findIndex((o) => o.toLowerCase().startsWith(a) || a.startsWith(o.toLowerCase()));
  if (i < 0) i = options.findIndex((o) => o.toLowerCase().includes(a));
  return i;
}

/**
 * Fills every empty field in `root`. Returns the list of fields it could not answer
 * (so the caller can pause for a human or give up on the job).
 */
export async function fillForm(root, profile, job) {
  const fields = await collectFields(root);
  const empty = fields.filter((f) => !String(f.value ?? "").trim());
  const prefilled = fields.filter((f) => String(f.value ?? "").trim());
  if (prefilled.length) log("dim", `   already filled: ${prefilled.map((f) => `${f.label.slice(0, 30)} = ${String(f.value).slice(0, 30)}`).join(" · ")}`);
  if (!fields.length) log("dim", "   (no form fields on this step)");
  if (!empty.length) return [];

  const needLlm = [];
  for (const f of empty) {
    const q = quickAnswer(f, profile);
    if (q) {
      const ok = await fillOne(root, f, q).catch(() => false);
      if (ok) log("dim", `   ↳ ${f.label.slice(0, 70)} → ${q}`);
      else needLlm.push(f);
    }
    else if (f.required || f.type !== "checkbox") needLlm.push(f);
  }
  if (!needLlm.length) return [];

  let answers = {};
  try {
    answers = await answerQuestions(profile, job, needLlm.map(({ key, label, type, options, required }) => ({ key, label, type, options, required })));
  } catch (e) {
    log("warn", `   Claude couldn't answer the questions (${e.message.split("\n")[0]})`);
  }
  const unanswered = [];
  for (const f of needLlm) {
    const ans = answers[f.key];
    if (!ans || ans === "__ASK__") {
      if (f.required) unanswered.push(f);
      continue;
    }
    log("dim", `   ↳ ${f.label.slice(0, 70)} → ${ans}`);
    const ok = await fillOne(root, f, ans).catch(() => false);
    if (!ok && f.required) unanswered.push(f);
    await humanPause(200, 600);
  }
  return unanswered;
}

/**
 * Custom dropdowns that aren't <select>: Workday's "Select One" buttons, React-Select /
 * Greenhouse comboboxes, Workday multiselect prompts ("How did you hear about us?").
 * Opens each empty one to read its options, asks Claude, then picks the answer.
 * Returns labels of required dropdowns it couldn't fill.
 */
export async function fillCustomSelects(root, profile, job) {
  const page = root.page();
  const triggers = root.locator("button[aria-haspopup=listbox], [role=combobox]:not(select)").filter({ visible: true });
  const n = Math.min(await triggers.count().catch(() => 0), 40);
  const items = [];
  for (let i = 0; i < n; i++) {
    const t = triggers.nth(i);
    const info = await t.evaluate((el) => {
      const clean = (s) => (s || "").replace(/\s+/g, " ").replace(/\*/g, "").trim();
      const byId = (id) => el.getRootNode()?.getElementById?.(id) || document.getElementById(id);
      const lab = el.getAttribute("aria-labelledby")?.split(" ").map((id) => byId(id)?.innerText || "").join(" ")
        || el.getAttribute("aria-label")
        || (el.id && document.querySelector(`label[for="${CSS.escape(el.id)}"]`)?.innerText)
        || el.closest("[data-automation-id^=formField], .field, .form-group, fieldset, div")?.querySelector("label, legend")?.innerText || "";
      const value = el.tagName === "INPUT" ? el.value : el.innerText;
      const wrap = el.closest("[data-automation-id^=formField], .field, .form-group, fieldset, div");
      return {
        label: clean(lab),
        value: clean(value),
        required: el.getAttribute("aria-required") === "true" || /\*/.test(wrap?.innerText?.slice(0, 200) || ""),
        isInput: el.tagName === "INPUT",
        multi: !!el.closest("[data-automation-id=multiselectInputContainer]"),
      };
    }).catch(() => null);
    if (!info || !info.label) continue;
    if (info.value && !/^(select( one)?|select\.\.\.|choose|please select|--)$/i.test(info.value) && !info.isInput) continue;
    if (info.isInput && info.value) continue;
    // Open dropdowns to read their options. Search boxes only show options after typing.
    let options = [];
    if (!info.isInput) {
      await t.click({ timeout: 2000 }).catch(() => {});
      await page.waitForTimeout(500);
      options = (await page.getByRole("option").filter({ visible: true }).allInnerTexts().catch(() => [])).map((o) => o.trim()).filter(Boolean).slice(0, 80);
      await page.keyboard.press("Escape").catch(() => {});
      if (await page.getByRole("listbox").filter({ visible: true }).count().catch(() => 0)) await t.click({ timeout: 1000 }).catch(() => {});
    }
    items.push({ i, ...info, options });
  }
  if (!items.length) return [];

  const fields = items.map((it) => ({ key: `cs${it.i}`, label: it.label, type: "select", options: it.options, required: it.required }));
  let answers = {};
  const quick = {};
  for (const f of fields) {
    const q = quickAnswer(f, profile);
    if (q) quick[f.key] = q;
  }
  const rest = fields.filter((f) => !quick[f.key]);
  if (rest.length) {
    try {
      answers = await answerQuestions(profile, job, rest);
    } catch (e) {
      log("warn", `   Claude couldn't answer the dropdowns (${e.message.split("\n")[0]})`);
    }
  }
  const missing = [];
  for (const it of items) {
    const key = `cs${it.i}`;
    const ans = quick[key] ?? answers[key];
    if (!ans || ans === "__ASK__") {
      if (it.required) missing.push({ label: it.label });
      continue;
    }
    const t = triggers.nth(it.i);
    if (process.env.JA_DEBUG) log("dim", `   [debug] ${it.label}: answer=${ans} options=${it.options.length}`);
    await t.click({ timeout: 2000 }).catch(() => {});
    if (it.isInput) {
      await t.fill("").catch(() => {});
      await t.pressSequentially(ans, { delay: 20 }).catch(() => {});
      if (it.multi) await page.keyboard.press("Enter").catch(() => {});
      await page.waitForTimeout(700);
    }
    // Options may only load after typing; re-read them now.
    const live = (await page.getByRole("option").filter({ visible: true }).allInnerTexts().catch(() => [])).map((o) => o.trim()).filter(Boolean);
    const opts = live.length ? live : it.options;
    const idx = bestOption(opts, ans);
    // Never pick an arbitrary option for a dropdown; for a search box the first match is what we typed.
    const opt = idx >= 0 ? page.getByRole("option", { name: opts[idx], exact: true }).filter({ visible: true }).first() : it.isInput ? page.getByRole("option").filter({ visible: true }).first() : null;
    const ok = opt ? await opt.click({ timeout: 2500 }).then(() => true).catch(() => false) : false;
    if (!ok && it.isInput) await page.keyboard.press("Enter").catch(() => {});
    if (!ok && !it.isInput) {
      await page.keyboard.press("Escape").catch(() => {});
      if (it.required) missing.push({ label: it.label });
      continue;
    }
    log("dim", `   ↳ ${it.label.slice(0, 70)} → ${idx >= 0 ? opts[idx] : ans}`);
    await page.waitForTimeout(400);
  }
  return missing;
}
