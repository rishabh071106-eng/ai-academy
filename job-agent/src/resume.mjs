import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";
import { RESUME_DIR, slugify } from "./util.mjs";

const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const fmtDate = (d) => {
  if (!d || /present/i.test(d)) return "Present";
  const [y, m] = String(d).split("-");
  return m ? new Date(+y, +m - 1).toLocaleString("en-GB", { month: "short", year: "numeric" }) : y;
};

export function renderResumeHtml(profile, t) {
  const contact = [profile.phone && `${profile.phoneCountryCode ?? ""} ${profile.phone}`.trim(), profile.email, profile.address || profile.city, profile.linkedinUrl?.replace(/^https?:\/\/(www\.)?/, "")]
    .filter(Boolean).map(esc).join("<span class=sep>•</span>");
  return `<!doctype html><html><head><meta charset="utf-8"><title>${esc(profile.name)} – Resume</title>
<style>
  @page { size: A4; margin: 14mm 15mm; }
  * { box-sizing: border-box; }
  body { font: 10.2pt/1.42 "Segoe UI", "Helvetica Neue", Arial, sans-serif; color: #1d1d1f; margin: 0; }
  header { border-bottom: 2px solid #0f5c63; padding-bottom: 8px; margin-bottom: 10px; }
  h1 { font: 700 24pt/1.1 Georgia, "Times New Roman", serif; margin: 0; letter-spacing: -.3px; }
  .tagline { color: #52514e; font-size: 9.5pt; margin-top: 2px; }
  .headline { color: #0f5c63; font-weight: 600; font-size: 11pt; margin-top: 2px; }
  .contact { color: #52514e; font-size: 9pt; margin-top: 5px; }
  .sep { margin: 0 6px; color: #b0aea8; }
  h2 { font-size: 10pt; text-transform: uppercase; letter-spacing: 1.2px; color: #0f5c63; margin: 13px 0 5px; }
  p { margin: 0; }
  .skills { display: flex; flex-wrap: wrap; gap: 4px 5px; }
  .skills span { background: #e4f0f0; color: #0b4a50; border-radius: 3px; padding: 1px 7px; font-size: 8.8pt; }
  .job { margin-bottom: 8px; page-break-inside: avoid; }
  .job-head { display: flex; justify-content: space-between; gap: 8px; }
  .role { font: 700 10.8pt Georgia, "Times New Roman", serif; }
  .company { color: #52514e; }
  .dates { color: #52514e; font-size: 9pt; white-space: nowrap; }
  ul { margin: 3px 0 0; padding-left: 16px; }
  li { margin: 1.5px 0; }
  .row { display: flex; justify-content: space-between; }
</style></head><body>
<header>
  <h1>${esc(profile.name)}</h1>
  <div class="headline">${esc(t.headline || profile.headline)}</div>
  ${profile.tagline ? `<div class="tagline">${esc(profile.tagline)}</div>` : ""}
  <div class="contact">${contact}</div>
</header>
<h2>Summary</h2><p>${esc(t.summary || profile.summary)}</p>
<h2>Skills</h2><div class="skills">${(t.skills?.length ? t.skills : profile.skills).map((s) => `<span>${esc(s)}</span>`).join("")}</div>
<h2>Experience</h2>
${(t.experience?.length ? t.experience : profile.experience).map((e) => `<div class="job">
  <div class="job-head"><div><span class="role">${esc(e.role)}</span> <span class="company">· ${esc(e.company)}${e.location ? ", " + esc(e.location) : ""}</span></div>
  <div class="dates">${fmtDate(e.start)} – ${fmtDate(e.end)}</div></div>
  <ul>${e.bullets.map((b) => `<li>${esc(b)}</li>`).join("")}</ul></div>`).join("")}
<h2>Education</h2>
${(profile.education ?? []).map((e) => `<div class="row"><div><b>${esc(e.degree)}</b> · ${esc(e.institution)}</div><div class="dates">${esc(e.start)} – ${esc(e.end)}</div></div>`).join("")}
${profile.certifications?.length ? `<h2>Certifications</h2>${profile.certifications.map((c) => `<div class="row"><div>${esc(c.name)}</div><div class="dates">${fmtDate(c.date)}</div></div>`).join("")}` : ""}
</body></html>`;
}

let pdfBrowser;
async function getPdfBrowser() {
  if (pdfBrowser) return pdfBrowser;
  // PDF printing needs headless Chromium; reuse the locally installed Chrome when possible.
  const attempts = [{ channel: "chrome" }, { channel: "msedge" }, {}];
  if (process.env.CHROME_PATH) attempts.unshift({ executablePath: process.env.CHROME_PATH });
  for (const opts of attempts) {
    try {
      pdfBrowser = await chromium.launch({ headless: true, ...opts });
      return pdfBrowser;
    } catch {}
  }
  throw new Error("Could not start headless Chrome for PDF rendering. Set CHROME_PATH in .env to your chrome executable.");
}

/** Writes data/resumes/<job>/<Name>_Resume.pdf (+ .html) and returns the absolute PDF path. */
export async function buildResumePdf(profile, tailored, job) {
  // One folder per job; the file itself gets a recruiter-friendly name.
  const dir = path.join(RESUME_DIR, `${job.platform}-${job.jobId}-${slugify(job.company)}`.slice(0, 100));
  fs.mkdirSync(dir, { recursive: true });
  const fileBase = `${profile.name.trim().replace(/[^A-Za-z0-9]+/g, "_")}_Resume`;
  const html = renderResumeHtml(profile, tailored ?? {});
  const htmlPath = path.join(dir, `${fileBase}.html`);
  const pdfPath = path.join(dir, `${fileBase}.pdf`);
  fs.writeFileSync(htmlPath, html);
  const browser = await getPdfBrowser();
  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: "load" });
  await page.pdf({ path: pdfPath, format: "A4", printBackground: true, preferCSSPageSize: true });
  await page.close();
  return pdfPath;
}

export async function closePdfBrowser() {
  await pdfBrowser?.close();
  pdfBrowser = undefined;
}
