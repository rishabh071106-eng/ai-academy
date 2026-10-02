// A small "look at the page, decide, act" loop for sites whose layout we don't know in
// advance (Alignerr, unusual career sites). Each step takes a compact snapshot of what is on
// screen (headings, text, numbered buttons/links/fields), asks Claude for ONE next action,
// and performs it. Forms are filled with the same filler as everywhere else; the tailored
// resume is uploaded through file inputs or the browser's file chooser.
import Anthropic from "@anthropic-ai/sdk";
import { fillCustomSelects, fillForm } from "./forms.mjs";
import { ask, confirm, loadConfig, log, sleep, stopIfFatalApiError } from "./util.mjs";

const client = new Anthropic();
// The click-by-click decisions can run on a cheaper model (config.navigatorModel).
const MODEL = loadConfig().navigatorModel || loadConfig().model || "claude-opus-5-5";

/** Numbers every visible interactive element (data-ja-ui) and returns a text snapshot. */
export async function snapshot(page) {
  return page.evaluate(() => {
    const clean = (s) => (s || "").replace(/\s+/g, " ").trim();
    const visible = (el) => {
      const r = el.getBoundingClientRect();
      const st = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && st.visibility !== "hidden" && st.display !== "none";
    };
    const deepAll = (node, sel) => {
      const out = [...node.querySelectorAll(sel)];
      for (const el of node.querySelectorAll("*")) if (el.shadowRoot) out.push(...deepAll(el.shadowRoot, sel));
      return out;
    };
    document.querySelectorAll("[data-ja-ui]").forEach((e) => e.removeAttribute("data-ja-ui"));
    const sel = "a[href], button, [role=button], [role=link], [role=tab], [role=menuitem], [role=option], [role=checkbox], [role=radio], [role=combobox], input:not([type=hidden]), select, textarea, [contenteditable=true]";
    const els = [];
    let n = 0;
    for (const el of deepAll(document, sel)) {
      if (n >= 160) break;
      const isFile = el.matches("input[type=file]");
      if (!isFile && !visible(el)) continue;
      const id = `e${n++}`;
      el.setAttribute("data-ja-ui", id);
      const tag = el.tagName.toLowerCase();
      const label =
        (el.labels && el.labels[0] && el.labels[0].innerText) || el.getAttribute("aria-label") || el.getAttribute("placeholder") || el.getAttribute("title") || el.getAttribute("name") || "";
      const text = clean(el.innerText || el.value || "").slice(0, 120);
      els.push({
        id,
        tag,
        role: el.getAttribute("role") || "",
        type: el.getAttribute("type") || "",
        text,
        label: clean(label).slice(0, 120),
        value: tag === "input" || tag === "textarea" || tag === "select" ? clean(el.value).slice(0, 60) : "",
        checked: el.checked || el.getAttribute("aria-checked") === "true" || undefined,
        href: tag === "a" ? el.getAttribute("href") : undefined,
        disabled: el.disabled || el.getAttribute("aria-disabled") === "true" || undefined,
      });
    }
    const headings = [...document.querySelectorAll("h1, h2, h3, [role=heading]")].filter(visible).map((h) => clean(h.innerText)).filter(Boolean).slice(0, 30);
    const main = document.querySelector("main, [role=main]") || document.body;
    return { url: location.href, title: document.title, headings, text: clean(main.innerText).slice(0, 7000), elements: els };
  });
}

const obj = (properties) => ({ type: "object", properties, required: Object.keys(properties), additionalProperties: false });
const str = { type: "string" };
const STEP_SCHEMA = obj({
  reasoning: { type: "string", description: "One short sentence: what you see and why this action" },
  action: { type: "string", enum: ["click", "type", "select", "fill_form", "upload_resume", "scroll", "back", "goto", "report_jobs", "done", "need_user"] },
  target: { type: "string", description: "Element id like e12, or empty" },
  value: { type: "string", description: "Text to type / option to select / URL for goto, or empty" },
  jobs: { type: "array", description: "Only for report_jobs: every role on the page", items: obj({ title: str, target: str, href: str, summary: str, already_applied: { type: "boolean" } }) },
  status: { type: "string", enum: ["applied", "already_applied", "not_eligible", "needs_user", "none"] },
  message: { type: "string", description: "For done / need_user: what happened or what the user must do" },
});

async function decide({ goal, rules, snap, history, profile, job }) {
  const { applicationAnswers, ...resume } = profile;
  const res = await client.beta.messages.create({
    model: MODEL,
    max_tokens: 6000,
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    output_config: { effort: "low", format: { type: "json_schema", schema: STEP_SCHEMA } },
    system: `You operate a web browser for Aishwarya Sharma to find and apply for work. Choose exactly ONE next action.
Actions: click(target) · type(target, value) · select(target, value) · fill_form (fills every empty field on the page from her data — use it as soon as an application form is visible) · upload_resume(target = the file input or the upload button/area) · scroll · back · goto(value=url) · report_jobs(jobs) · done(status, message) · need_user(message).
Rules:
- Use only true information from her data. Never invent facts.
- Never take skill assessments, tests, quizzes, coding challenges, AI/video interviews, or ID verification for her: when one is required, use need_user (or done with status "applied" if the application itself was already submitted).
- Never pay, never change account/security settings, never delete anything, never log out.
- Accept routine application consents/terms needed to apply.
- Close cookie banners and pop-ups that block the page.
- If the same action didn't change anything twice, try something else; if stuck, need_user.
${rules || ""}`,
    messages: [
      {
        role: "user",
        content: `GOAL: ${goal}
${job ? `ROLE: ${job.title}${job.company ? ` at ${job.company}` : ""}` : ""}

HER DATA (short):
${JSON.stringify({ name: resume.name, email: resume.email, phone: resume.phone, city: resume.city, headline: resume.headline, skills: resume.skills, experienceYears: resume.totalExperienceYears, answers: applicationAnswers }, null, 1).slice(0, 3000)}

RECENT ACTIONS:
${history.slice(-8).map((h, i) => `${i + 1}. ${h}`).join("\n") || "(none)"}

PAGE: ${snap.title} — ${snap.url}
Headings: ${snap.headings.join(" | ")}
Text: ${snap.text.slice(0, 5000)}

ELEMENTS:
${snap.elements.map((e) => `${e.id} ${e.tag}${e.role ? `[${e.role}]` : ""}${e.type ? `(${e.type})` : ""}${e.disabled ? " disabled" : ""}${e.checked ? " checked" : ""} "${e.text || e.label}"${e.label && e.text ? ` label="${e.label}"` : ""}${e.value ? ` value="${e.value}"` : ""}${e.href ? ` href=${e.href.slice(0, 100)}` : ""}`).join("\n")}`,
      },
    ],
  });
  if (res.stop_reason === "refusal") throw new Error("Claude declined this step");
  return JSON.parse(res.content.filter((b) => b.type === "text").map((b) => b.text).join(""));
}

const el = (page, id) => page.locator(`[data-ja-ui="${id}"]`).first();

/**
 * Work towards `goal` on the current page. Returns { status, note, jobs? }.
 * opts: { goal, rules, profile, job, resumePath, mode, maxSteps, stopOnReport }
 */
export async function navigate(page, opts) {
  const { goal, profile, job, resumePath, mode = "review", maxSteps = 30, stopOnReport = false } = opts;
  const history = [];
  let reported = [];
  for (let step = 0; step < maxSteps; step++) {
    await page.waitForLoadState("domcontentloaded").catch(() => {});
    await sleep(1200);
    const snap = await snapshot(page).catch(() => null);
    if (!snap) {
      await sleep(1500);
      continue;
    }
    let d;
    try {
      d = await decide({ goal, rules: opts.rules, snap, history, profile, job });
    } catch (e) {
      stopIfFatalApiError(e);
      log("warn", `   navigator: ${e.message.split("\n")[0]}`);
      return { status: "needs_attention", note: `Couldn't decide the next step (${e.message.split("\n")[0]})` };
    }
    const target = d.target ? snap.elements.find((x) => x.id === d.target) : null;
    const desc = `${d.action}${target ? ` "${(target.text || target.label).slice(0, 50)}"` : ""}${d.value && d.action !== "type" ? ` ${d.value.slice(0, 60)}` : d.value ? ` = ${d.value.slice(0, 40)}` : ""}`;
    log("dim", `   → ${desc}  (${d.reasoning.slice(0, 90)})`);
    history.push(`${desc} — on "${snap.title}"`);

    try {
      switch (d.action) {
        case "click": {
          const isSubmit = /submit|send application|finish|complete application|^apply$/i.test(target?.text || target?.label || "");
          if (isSubmit && mode !== "auto" && /submit|send|finish|complete/i.test(target?.text || target?.label || "")) {
            if (!(await confirm(`Submit the application${job ? ` for ${job.title}` : ""}?`))) return { status: "skipped", note: "You chose not to submit" };
          }
          const popup = page.context().waitForEvent("page", { timeout: 2500 }).catch(() => null);
          await el(page, d.target).click({ timeout: 6000 });
          const tab = await popup;
          if (tab) {
            log("dim", "   (opened in a new tab; continuing there)");
            await tab.waitForLoadState("domcontentloaded").catch(() => {});
            return navigate(tab, { ...opts, maxSteps: maxSteps - step - 1 });
          }
          break;
        }
        case "type":
          await el(page, d.target).fill(d.value, { timeout: 5000 });
          break;
        case "select": {
          const t = el(page, d.target);
          if ((await t.evaluate((x) => x.tagName).catch(() => "")) === "SELECT") await t.selectOption({ label: d.value }).catch(() => t.selectOption(d.value));
          else {
            await t.click();
            await page.getByRole("option", { name: d.value }).first().click({ timeout: 4000 });
          }
          break;
        }
        case "fill_form": {
          const root = page.locator("body");
          const missing = [...(await fillForm(root, profile, job || {})), ...(await fillCustomSelects(root, profile, job || {}))];
          if (missing.length) history.push(`fill_form left these empty: ${missing.map((m) => m.label).join("; ")}`);
          break;
        }
        case "upload_resume": {
          if (!resumePath) {
            history.push("no resume file available");
            break;
          }
          const t = d.target ? el(page, d.target) : page.locator("input[type=file]").first();
          const isInput = await t.evaluate((x) => x.tagName === "INPUT" && x.type === "file").catch(() => false);
          if (isInput) await t.setInputFiles(resumePath);
          else {
            const chooser = page.waitForEvent("filechooser", { timeout: 6000 });
            await t.click();
            await (await chooser).setFiles(resumePath);
          }
          log("dim", "   ↳ uploaded tailored resume");
          await sleep(2500);
          break;
        }
        case "scroll":
          await page.mouse.wheel(0, 1200);
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
          return { status: d.status === "already_applied" ? "applied" : d.status === "not_eligible" ? "skipped" : d.status === "applied" ? "applied" : "needs_attention", note: d.message || d.status, jobs: reported };
        case "need_user": {
          if (mode === "auto") return { status: "needs_attention", note: d.message };
          await page.bringToFront().catch(() => {});
          const r = await ask(`${job ? `${job.title}: ` : ""}${d.message}`, [
            { label: "Done, continue", value: "" },
            { label: "It's applied", value: "done" },
            { label: "Skip", value: "s" },
          ]);
          if (r === "done") return { status: "applied", note: "Finished by you" };
          if (r === "s") return { status: "needs_attention", note: d.message };
          history.push("the user handled the request; continue");
          break;
        }
      }
    } catch (e) {
      history.push(`that failed: ${e.message.split("\n")[0].slice(0, 120)}`);
    }
  }
  return { status: "needs_attention", note: "Ran out of steps", jobs: reported };
}
