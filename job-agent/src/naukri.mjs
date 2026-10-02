import { firstVisible, textOf } from "./browser.mjs";
import { answerQuestions } from "./llm.mjs";
import { confirm, humanPause, log, sleep, slugify, waitForUser } from "./util.mjs";

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
      return { jobId: e.getAttribute("data-job-id") || a?.href.match(/-(\d{9,})/)?.[1], url: a?.href };
    }).filter((j) => j.jobId && j.url));
  return jobs.slice(0, cfg.max);
}

export async function getJob(page, ref) {
  await page.goto(ref.url, { waitUntil: "domcontentloaded" });
  await firstVisible(page, ["h1"], 15000);
  await humanPause();
  const applyBtn = await firstVisible(page, ["#apply-button", "button[class*=apply-button]", "button:has-text('Apply')"]);
  const applyText = applyBtn ? (await applyBtn.innerText()).trim() : "";
  const external = await firstVisible(page, ["#company-site-button", "button:has-text('Apply on company site')"]);
  return {
    ...ref,
    title: await textOf(page, ["h1[class*=jd-header-title]", "h1"]),
    company: (await textOf(page, ["[class*=jd-header-comp-name] a", "[class*=jd-header-comp-name]"])).split("\n")[0],
    location: await textOf(page, ["[class*=jhc__location]", "[class*=location] a", "[class*=loc]"]),
    description: await textOf(page, ["[class*=job-desc]", "[class*=dang-inner-html]", "section[class*=JD]", "main"]),
    alreadyApplied: /^applied$/i.test(applyText),
    applyType: external ? "external" : applyBtn ? "easy" : "none",
  };
}

const SUCCESS = ["text=/successfully applied/i", "text=/applied to/i", "[class*=apply-message]:has-text('Applied')"];
const CHAT = "[class*=chatbot_Drawer], [class*=chatbot_MessageContainer], .chatbot_DrawerContentWrapper";

export async function apply(page, job, { profile, mode }) {
  const btn = await firstVisible(page, ["#apply-button", "button[class*=apply-button]", "button:has-text('Apply')"], 5000);
  if (!btn) return { status: "needs_attention", note: "Apply button not found" };
  if (mode !== "auto") {
    if (!(await confirm(`Apply on Naukri to ${job.company} – ${job.title}? (uses the resume on your Naukri profile)`))) return { status: "skipped", note: "You chose not to apply" };
  }
  await btn.click();
  await sleep(2500);

  for (let turn = 0; turn < 20; turn++) {
    if (await firstVisible(page, SUCCESS, 1500)) return { status: "applied", note: "Naukri apply" };
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
  return (await firstVisible(page, SUCCESS, 4000))
    ? { status: "applied", note: "Naukri apply" }
    : { status: "needs_attention", note: "No confirmation after Apply — check Naukri > Applies" };
}
