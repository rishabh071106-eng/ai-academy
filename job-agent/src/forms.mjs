// Generic form reading/filling for application modals (LinkedIn Easy Apply, Naukri questionnaires).
import { answerQuestions } from "./llm.mjs";
import { humanPause, log } from "./util.mjs";

/**
 * Reads every visible, fillable field inside `root` and tags it with data-ja-key.
 * Returns [{ key, label, type, required, value, options? }].
 */
export async function collectFields(root) {
  return root.evaluate((rootEl) => {
    const visible = (el) => !!(el && (el.offsetParent || el.getClientRects().length));
    const clean = (s) => (s || "").replace(/\s+/g, " ").replace(/\*/g, "").trim();
    const labelOf = (el) => {
      if (el.labels && el.labels[0]) return clean(el.labels[0].innerText);
      const by = el.getAttribute("aria-labelledby");
      if (by) return clean(by.split(" ").map((id) => document.getElementById(id)?.innerText || "").join(" "));
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
    for (const el of rootEl.querySelectorAll("input, select, textarea")) {
      const type = (el.tagName === "INPUT" ? el.type || "text" : el.tagName).toLowerCase();
      if (["hidden", "submit", "button", "file", "search", "image", "reset"].includes(type)) continue;
      if (el.disabled || el.readOnly) continue;
      if (type === "radio") {
        const name = el.name || el.id;
        if (seenRadio.has(name)) continue;
        seenRadio.add(name);
        const group = [...rootEl.querySelectorAll(`input[type=radio][name="${CSS.escape(name)}"]`)];
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
function quickAnswer(field, profile) {
  const l = field.label.toLowerCase();
  const [first, ...rest] = profile.name.split(" ");
  if (/e-?mail/.test(l)) return profile.email;
  if (/country code/.test(l)) return field.options?.find((o) => o.includes("India") || o.includes("+91")) ?? null;
  if (/mobile|phone/.test(l)) return profile.phone;
  if (/first name/.test(l)) return first;
  if (/last name|surname/.test(l)) return rest.join(" ");
  if (/^(full )?name$/.test(l)) return profile.name;
  if (/linkedin/.test(l) && profile.linkedinUrl) return profile.linkedinUrl;
  if (/^(location|city|current city|location \(city\))$/.test(l)) return profile.city;
  if (/total (years of )?(work )?experience|overall experience/.test(l) && field.type !== "select") return String(profile.totalExperienceYears);
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
  await el.first().fill("");
  await el.first().pressSequentially(String(answer), { delay: 25 });
  // Typeahead fields (e.g. city) show a suggestion list; pick the first suggestion.
  const option = page.locator("[role=listbox] [role=option], .basic-typeahead__selectable, .search-typeahead-v2__hit").first();
  if (await option.isVisible({ timeout: 1200 }).catch(() => false)) await option.click();
  return true;
}

function bestOption(options = [], answer) {
  const a = String(answer).trim().toLowerCase();
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
  if (!empty.length) return [];

  const needLlm = [];
  for (const f of empty) {
    const q = quickAnswer(f, profile);
    if (q) await fillOne(root, f, q).catch(() => needLlm.push(f));
    else if (f.required || f.type !== "checkbox") needLlm.push(f);
  }
  if (!needLlm.length) return [];

  const answers = await answerQuestions(profile, job, needLlm.map(({ key, label, type, options, required }) => ({ key, label, type, options, required })));
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
