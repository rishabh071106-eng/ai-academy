// Reads the verification code or confirmation link a job site just emailed her, from Gmail
// open in the agent's Chrome (log in to Gmail once in that Chrome window). Used when a career
// site says "we sent a code / link to your email" (Workday, Photon, iCIMS, SuccessFactors…),
// so the application can carry on without a person. Only the newest matching emails are read,
// and only to extract that code or link.
import { generateJSON } from "./ai.mjs";
import { isSkip, loadConfig, log, sleep } from "./util.mjs";

const SCHEMA = {
  type: "object",
  properties: {
    found: { type: "boolean", description: "true if this email is the verification/sign-up email for this site" },
    code: { type: "string", description: "The verification code / OTP, or empty" },
    link: { type: "string", description: "The verify/activate/confirm-account link, or empty" },
  },
  required: ["found", "code", "link"],
  additionalProperties: false,
};

/** Subject, text and links of the newest Gmail messages matching `query` (newest first). */
async function readInbox(tab, query, max = 3) {
  await tab.goto(`https://mail.google.com/mail/u/0/#search/${encodeURIComponent(query)}`, { waitUntil: "domcontentloaded" });
  await sleep(2500);
  if (/accounts\.google\.com/.test(tab.url())) throw new Error("Gmail isn't logged in in the agent's Chrome — open mail.google.com there and sign in once");
  const rows = tab.locator("tr.zA").filter({ visible: true });
  await rows.first().waitFor({ timeout: 15000 }).catch(() => {});
  const n = Math.min(await rows.count().catch(() => 0), max);
  const mails = [];
  for (let i = 0; i < n; i++) {
    await rows.nth(i).click({ timeout: 5000 }).catch(() => {});
    const body = tab.locator(".a3s").filter({ visible: true }).last();
    await body.waitFor({ timeout: 10000 }).catch(() => {});
    const text = (await body.innerText().catch(() => "")).slice(0, 4000);
    const subject = await tab.locator("h2.hP").first().innerText().catch(() => "");
    const links = await body
      .locator("a[href]")
      .evaluateAll((as) => as.map((a) => ({ text: a.innerText.trim().slice(0, 60), href: a.href })).filter((l) => /^https?:/.test(l.href)).slice(0, 25))
      .catch(() => []);
    if (text) mails.push({ subject, text, links });
    await tab.goBack().catch(() => {});
    await sleep(1200);
  }
  return mails;
}

/**
 * Waits (up to ~3 minutes) for the site's email and returns { code, link } or null.
 * `hint` = company / site name, e.g. "Photon" or "myworkdayjobs".
 */
export async function readVerificationEmail(context, hint = "") {
  if (loadConfig().readVerificationEmails === false) return null;
  const tab = await context.newPage();
  try {
    for (let attempt = 0; attempt < 7; attempt++) {
      const queries = [...(hint ? [`newer_than:1h ${hint}`] : []), "newer_than:1h (verify OR verification OR code OR OTP OR activate OR confirm)"];
      for (const q of queries) {
        const mails = await readInbox(tab, q);
        for (const m of mails) {
          const r = await generateJSON({
            role: "navigator",
            effort: "low",
            maxTokens: 1500,
            schema: SCHEMA,
            system:
              "You read one email and extract the account verification code or the verify/activate link that a job/career website sent. Only report found=true if the email is clearly that verification email (for the site named, if any). Never invent a code.",
            content: `SITE: ${hint || "(unknown)"}\nSUBJECT: ${m.subject}\nEMAIL:\n${m.text}\n\nLINKS:\n${m.links.map((l) => `${l.text} → ${l.href}`).join("\n")}`,
          }).catch(() => null);
          if (r?.found && (r.code || r.link)) {
            log("dim", `   ↳ found the ${r.code ? "verification code" : "verification link"} in Gmail ("${m.subject.slice(0, 60)}")`);
            return { code: r.code || "", link: r.link || "" };
          }
        }
      }
      log("dim", "   (waiting for the verification email…)");
      await sleep(25000);
    }
    return null;
  } catch (e) {
    if (isSkip(e)) throw e;
    log("warn", `   couldn't read Gmail: ${e.message.split("\n")[0]}`);
    return null;
  } finally {
    await tab.close().catch(() => {});
  }
}

/** Opens a verify/activate link in its own tab, waits for it to load, and closes it again. */
export async function openVerificationLink(context, link) {
  const tab = await context.newPage();
  try {
    await tab.goto(link, { waitUntil: "domcontentloaded", timeout: 30000 });
    await sleep(4000);
    return (await tab.locator("body").innerText().catch(() => "")).slice(0, 300);
  } finally {
    await tab.close().catch(() => {});
  }
}
