import { expandJob, firstVisible, readPage, textOf } from "./browser.mjs";
import { answerQuestions } from "./llm.mjs";
import fs from "node:fs";
import path from "node:path";
import { ask, confirm, DATA_DIR, humanPause, log, sleep, slugify, waitForUser } from "./util.mjs";

export const name = "naukri";

export async function search(page, s, cfg) {
  const remote = /remote|wfh/i.test(s.location ?? "");
  const slug = slugify(s.keywords) + "-jobs" + (s.location && !remote ? `-in-${slugify(s.location)}` : "");
  const params = new URLSearchParams({ k: s.keywords });
  if (s.location && !remote) params.set("l", s.location);
  if (remote) params.set("wfhType", "2");
  if (cfg.experienceYears != null) params.set("experience", String(cfg.experienceYears));
  if (cfg.postedWithinDays) params.set("jobAge", String(cfg.postedWithinDays));
  await page.goto(`https://www.naukri.com/${slug}?${params}`, { waitUntil: "domcontentloaded" });
  await firstVisible(page, [".srp-jobtuple-wrapper", "article.jobTuple", "[class*=no-result]"], 15000);

  const jobs = await page.$$eval(".srp-jobtuple-wrapper, article.jobTuple", (els) =>
    els.map((e) => {
      const a = e.querySelector("a.title, a[class*=title]");
      return { jobId: e.getAttribute("data-job-id") || a?.href.match(/-(\d{9,})/)?.[1], url: a?.href, cardText: (e.innerText || "").replace(/\s+/g, " ").trim().slice(0, 300) };
    }).filter((j) => j.jobId && j.url));
  return jobs.slice(0, cfg.max);
}

export async function getJob(page, ref) {
  await page.goto(ref.url, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("load", { timeout: 15000 }).catch(() => {});
  await firstVisible(page, ["h1", "main"], 15000);
  await humanPause(1200, 2200);
  const expanded = await expandJob(page, "body");
  const { h1, pageText } = await readPage(page);
  const applyBtn = await firstVisible(page, ["#apply-button", "button[class*=apply-button]", "button:has-text('Apply')"]);
  const applyText = applyBtn ? (await applyBtn.innerText()).trim() : "";
  const external = await firstVisible(page, ["#company-site-button", "button:has-text('Apply on company site')"]);
  const description = await textOf(page, ["[class*=job-desc]", "[class*=dang-inner-html]", "section[class*=JD]"]);
  return {
    ...ref,
    title: h1,
    company: (await textOf(page, ["[class*=jd-header-comp-name] a", "[class*=jd-header-comp-name]"])).split("\n")[0],
    location: await textOf(page, ["[class*=jhc__location]", "[class*=location] a", "[class*=loc]"]),
    description: description.length > 300 ? description : pageText,
    pageTextLength: pageText.length,
    expanded,
    alreadyApplied: /^applied$/i.test(applyText),
    applyType: external ? "external" : applyBtn ? "easy" : "none",
  };
}

const SUCCESS = ["text=/successfully applied/i", "text=/applied to/i", "[class*=apply-message]:has-text('Applied')"];
const CHAT = "[class*=chatbot_Drawer], [class*=chatbot_MessageContainer], .chatbot_DrawerContentWrapper";

/**
 * Replaces the resume on her Naukri profile (Naukri's Apply always sends the profile resume).
 * Done in the same tab (no extra windows); pass `returnTo` to come back to the job afterwards.
 */
export async function uploadResume(page, pdfPath, returnTo) {
  try {
    await page.goto("https://www.naukri.com/mnjuser/profile", { waitUntil: "domcontentloaded" });
    await page.waitForLoadState("load", { timeout: 15000 }).catch(() => {});
    const input = page.locator("input#attachCV, input[type=file][id*=attach i], input[type=file][accept*=pdf i], input[type=file]").first();
    await input.waitFor({ state: "attached", timeout: 15000 });
    await input.setInputFiles(pdfPath);
    const ok = await firstVisible(page, ["text=/successfully uploaded|uploaded successfully|resume has been (successfully )?(uploaded|updated)/i"], 20000);
    await sleep(1500);
    return !!ok;
  } catch (e) {
    log("warn", `   resume upload failed: ${e.message.split("\n")[0]}`);
    return false;
  } finally {
    if (returnTo) {
      await page.goto(returnTo, { waitUntil: "domcontentloaded" }).catch(() => {});
      await page.waitForLoadState("load", { timeout: 15000 }).catch(() => {});
      await sleep(1500);
    }
  }
}

export async function apply(page, job, { profile, mode, resumePath, cfg = {} }) {
  const btn = await firstVisible(page, ["#apply-button", "button[class*=apply-button]", "button:has-text('Apply')"], 5000);
  if (!btn) return { status: "needs_attention", note: "Apply button not found" };
  if (mode !== "auto") {
    const which = cfg.uploadTailoredResume !== false && resumePath ? "with the resume tailored for this job" : "with the resume on your Naukri profile";
    if (!(await confirm(`Apply on Naukri to ${job.company} – ${job.title} ${which}?`))) return { status: "skipped", note: "You chose not to apply" };
  }
  let resumeNote = "profile resume";
  if (cfg.uploadTailoredResume !== false && resumePath) {
    log("dim", "   uploading tailored resume to your Naukri profile…");
    if (await uploadResume(page, resumePath, job.url)) {
      resumeNote = "tailored resume";
      apply.uploaded = true;
    } else {
      log("warn", "   couldn't confirm the upload; applying with whatever resume is on the profile");
    }
  }
  const applyBtn = (await firstVisible(page, ["#apply-button", "button[class*=apply-button]", "button:has-text('Apply')"], 8000)) ?? btn;
  await applyBtn.click();
  await sleep(2500);

  for (let turn = 0; turn < 20; turn++) {
    if (await firstVisible(page, SUCCESS, 1500)) return { status: "applied", note: `Naukri apply (${resumeNote})` };
    const chat = await firstVisible(page, [CHAT], 3000);
    if (!chat) break;

    // The recruiter questionnaire is a chat: answer the latest bot question.
    const question = await chat.evaluate((el) => {
      const msgs = el.querySelectorAll(".botMsg, [class*=botItem] span, [class*=botMsg]");
      return msgs.length ? msgs[msgs.length - 1].innerText.trim() : "";
    });
    const chips = chat.locator(".ssrc__radio-btn-container label, .chatbot_Chip, [class*=chipsContainer] [class*=chip], .mcc__checkbox label");
    const options = (await chips.allInnerTexts().catch(() => [])).map((t) => t.trim()).filter(Boolean);
    if (!question) break;

    const { q: answer } = await answerQuestions(profile, job, [{ key: "q", label: question, type: options.length ? "radio" : "text", options, required: true }]);
    if (!answer || answer === "__ASK__") {
      log("warn", `   Couldn't answer: "${question}"`);
      if (mode === "auto") return { status: "needs_attention", note: `Questionnaire: ${question}` };
      if (!(await waitForUser(`Naukri question for ${job.company}: "${question}". Answer it in Chrome, then continue.`))) return { status: "skipped", note: "Skipped by you at questionnaire" };
      continue;
    }
    log("dim", `   ↳ ${question.slice(0, 70)} → ${answer}`);
    if (options.length) {
      const a = answer.toLowerCase();
      let i = options.findIndex((o) => o.toLowerCase() === a);
      if (i < 0) i = options.findIndex((o) => o.toLowerCase().includes(a) || a.includes(o.toLowerCase()));
      if (i < 0) {
        if (mode === "auto") return { status: "needs_attention", note: `Questionnaire: ${question}` };
        if (!(await waitForUser(`Pick the answer for "${question}" in Chrome, then continue.`))) return { status: "skipped", note: "Skipped by you at questionnaire" };
        continue;
      }
      await chips.nth(i).click().catch(() => {});
    } else {
      const input = await firstVisible(chat, ["div.textArea[contenteditable]", "[contenteditable=true]", "input[type=text]", "textarea"]);
      if (!input) return { status: "needs_attention", note: `No input for: ${question}` };
      await input.click();
      await input.pressSequentially(answer, { delay: 30 });
    }
    await humanPause(500, 1000);
    const send = await firstVisible(chat, [".sendMsg", "[class*=sendMsg]", "button:has-text('Save')", "button:has-text('Submit')"]);
    await send?.click();
    await sleep(2000);
  }
  if (await firstVisible(page, SUCCESS, 4000)) return { status: "applied", note: `Naukri apply (${resumeNote})` };
  // Naukri sent us somewhere unexpected (extra form, company page, login). Don't silently move on.
  const shot = path.join(DATA_DIR, "debug", `naukri-${job.jobId}-apply.png`);
  fs.mkdirSync(path.dirname(shot), { recursive: true });
  await page.screenshot({ path: shot }).catch(() => {});
  log("warn", `   no confirmation after Apply (screenshot: data/debug/${path.basename(shot)})`);
  if (mode === "auto") return { status: "needs_attention", note: "No confirmation after Apply — check Naukri > Applies" };
  const r = await ask(`${job.company} – ${job.title}: Naukri didn't confirm the application. Finish it in Chrome if something is asked, then tell me.`, [
    { label: "It's applied", value: "done" },
    { label: "Skip this job", value: "s" },
  ]);
  return r === "done" ? { status: "applied", note: `Naukri apply, finished by you (${resumeNote})` } : { status: "needs_attention", note: "No confirmation after Apply" };
}
