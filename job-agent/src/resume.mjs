import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";
import { RESUME_DIR, slugify } from "./util.mjs";

// Text from Claude can carry markdown or stray symbols; clean it before it goes on the page.
const tidy = (s) =>
  String(s ?? "")
    .replace(/\\n/g, " ")
    .replace(/\*\*|__|`/g, "")
    .replace(/^\s*([-*•▪▸►●]|\d+[.)])\s+/, "")
    .replace(/[\u200B-\u200D\uFEFF\u0000-\u0008\u000B\u000C\u000E-\u001F\uFFFD]/g, "")
    .replace(/\s+/g, " ")
    .trim();
const esc = (s) => tidy(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const fmtDate = (d) => {
  if (!d) return "";
  if (/present/i.test(d)) return "Present";
  const [y, m] = String(d).split("-");
  return m ? new Date(+y, +m - 1).toLocaleString("en-GB", { month: "short", year: "numeric" }) : y;
};

// Bold lead-in like "Peelworks (Magento 2 Commerce, mobile + web): built …"
const bullet = (b) => {
  const m = tidy(b).match(/^([^:]{3,80}\)|[A-Z][^:]{2,40}):\s+(.*)$/s);
  return m ? `<b>${esc(m[1])}:</b> ${esc(m[2])}` : esc(b);
};
const role = (e) => `<div class="job">
  <div class="job-head"><div class="job-title">${esc(e.role)} <span class="at">· ${esc(e.company)}</span></div><div class="dates">${fmtDate(e.start)} – ${fmtDate(e.end)}</div></div>
  <div class="loc">${esc(e.location || "")}${e.client ? ` · Client: ${esc(e.client)}` : ""}</div>
  <ul>${(e.bullets || []).map((b) => `<li>${bullet(b)}</li>`).join("")}</ul></div>`;

/**
 * Mirrors her own resume: serif name, teal accents, two-column first page (summary +
 * recent roles | at-a-glance, grouped skills, certifications, education), then older roles,
 * the project index and credentials. Tailoring only changes the text, never the design.
 */
export function renderResumeHtml(profile, t = {}) {
  const exp = t.experience?.length ? t.experience : profile.experience || [];
  const groups = t.skillGroups?.length ? t.skillGroups : profile.skillGroups?.length ? profile.skillGroups : [{ name: "Skills", items: t.skills?.length ? t.skills : profile.skills || [] }];
  const firstPage = exp.slice(0, 2), later = exp.slice(2);
  const link = (profile.linkedinUrl || "").replace(/^https?:\/\/(www\.)?/, "").replace(/\/$/, "");
  const phone = profile.phone ? `${profile.phoneCountryCode ?? "+91"} ${String(profile.phone).replace(/(\d{5})(\d{5})/, "$1 $2")}` : "";
  const edu = (profile.education || []).map((e) => `<div class="edu ${e.status ? "pursuing" : ""}"><b>${esc(e.degree)}</b><div>${esc(e.institution)}${e.status ? ` · ${esc(e.status)}` : ""}</div><div class="mono">${fmtDate(e.start)} – ${fmtDate(e.end)}</div></div>`).join("");
  return `<!doctype html><html><head><meta charset="utf-8"><title>${esc(profile.name)} – Resume</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  @page { size: A4; margin: 13mm 13mm 12mm; }
  :root { --teal: #0f5c63; --tint: #e6f0f0; --ink: #1d1d1f; --mute: #5d6166; --rule: #d9dcdf; }
  * { box-sizing: border-box; }
  body { margin: 0; color: var(--ink); font: 9.6pt/1.45 "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif; }
  .serif { font-family: Fraunces, Georgia, "Times New Roman", serif; }
  .mono { font-family: "IBM Plex Mono", Menlo, monospace; font-size: 8.4pt; color: var(--mute); }
  header { display: flex; justify-content: space-between; gap: 18px; padding-bottom: 9px; border-bottom: 2.2px solid var(--teal); }
  h1 { font: 600 30pt/1.05 Fraunces, Georgia, serif; margin: 0; letter-spacing: -.4px; }
  .headline { color: var(--teal); font-weight: 600; font-size: 11.6pt; margin-top: 5px; }
  .tagline { color: var(--mute); font-size: 9.6pt; margin-top: 2px; max-width: 440px; }
  .contact { text-align: right; font-size: 9.4pt; line-height: 1.7; white-space: nowrap; padding-top: 4px; }
  h2 { font: 600 8.6pt/1 "IBM Plex Sans", sans-serif; letter-spacing: 2.2px; text-transform: uppercase; color: var(--teal); margin: 15px 0 7px; padding-bottom: 5px; border-bottom: 1px solid var(--rule); }
  h2 small { font-weight: 400; letter-spacing: 0; text-transform: none; color: var(--mute); margin-left: 4px; }
  .cols { display: grid; grid-template-columns: 1fr 255px; gap: 0 26px; }
  p { margin: 0; }
  .job { margin-bottom: 9px; break-inside: avoid; }
  .job-head { display: flex; justify-content: space-between; gap: 10px; align-items: baseline; }
  .job-title { font: 600 11.2pt/1.25 Fraunces, Georgia, serif; }
  .job-title .at { font-weight: 500; color: #3c4246; }
  .dates { font-family: "IBM Plex Mono", Menlo, monospace; font-size: 8.4pt; color: var(--mute); white-space: nowrap; }
  .loc { color: var(--mute); font-size: 9pt; margin: 1px 0 3px; }
  ul { margin: 0; padding-left: 13px; }
  li { margin: 2.5px 0; padding-left: 2px; }
  li::marker { color: var(--teal); font-size: 8pt; }
  .tiles { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
  .tile { background: var(--tint); border-radius: 4px; padding: 7px 8px; }
  .tile b { display: block; font: 600 17pt/1 Fraunces, Georgia, serif; color: var(--teal); }
  .tile span { font-size: 8.4pt; color: var(--mute); line-height: 1.25; display: block; margin-top: 3px; }
  .grp { margin-bottom: 8px; }
  .grp b { display: block; font-weight: 600; font-size: 9.6pt; margin-bottom: 1px; }
  .grp div { color: var(--mute); font-size: 9pt; }
  h2 { break-after: avoid; }
  .tile, .grp, .cert, .edu, .cred { break-inside: avoid; }
  .cert { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 7px; }
  .cert span { color: var(--mute); display: block; font-size: 9pt; }
  .edu { margin-bottom: 8px; }
  .edu div { color: var(--mute); font-size: 9pt; }
  .edu.pursuing { border-left: 3px solid var(--teal); padding-left: 8px; }
  .page2 { font-size: 9.3pt; margin-top: 4px; }
  html, body { height: auto; }
  body > :last-child, .page2 > :last-child { margin-bottom: 0; }
  .page2 h2 { margin-top: 12px; }
  .page2 .job { margin-bottom: 6px; }
  .creds { break-inside: avoid; }
  table { break-inside: auto; } tr { break-inside: avoid; }
  table { width: 100%; border-collapse: collapse; font-size: 8.9pt; }
  th { text-align: left; font-weight: 500; font-size: 7.8pt; letter-spacing: 1.4px; text-transform: uppercase; color: var(--mute); padding: 4px 8px; border-bottom: 1px solid var(--rule); }
  td { padding: 4px 8px; vertical-align: top; border-bottom: 1px solid var(--rule); color: #3c4246; }
  td:first-child { font-weight: 600; color: var(--ink); white-space: nowrap; }
  tr:nth-child(even) td { background: #f2f6f6; }
  .creds { display: grid; grid-template-columns: repeat(4, 1fr); gap: 7px; }
  .cred { border: 1px solid var(--rule); border-radius: 4px; padding: 6px 8px; font-size: 8.8pt; }
  .cred.on { border-color: var(--teal); background: var(--tint); }
  .cred small { display: block; font-size: 7.6pt; letter-spacing: 1.4px; text-transform: uppercase; color: var(--teal); font-weight: 600; margin-bottom: 4px; }
  .cred div { color: var(--mute); font-size: 8.6pt; margin-top: 3px; }
</style></head><body>
<header>
  <div><h1>${esc(profile.name)}</h1>
    <div class="headline">${esc(t.headline || profile.headline)}</div>
    ${t.tagline || profile.tagline ? `<div class="tagline">${esc(t.tagline || profile.tagline)}</div>` : ""}</div>
  <div class="contact">${[profile.email, phone, profile.address || profile.city, link].filter(Boolean).map(esc).join("<br>")}</div>
</header>
<div class="cols">
  <div>
    <h2>Summary</h2><p>${esc(t.summary || profile.summary)}</p>
    <h2>Experience</h2>${firstPage.map(role).join("")}
  </div>
  <aside>
    ${profile.highlights?.length ? `<h2>At a glance</h2><div class="tiles">${profile.highlights.slice(0, 3).map((h) => `<div class="tile"><b>${esc(h.value)}</b><span>${esc(h.label)}</span></div>`).join("")}</div>` : ""}
    <h2>Technical skills</h2>${groups.map((g) => `<div class="grp"><b>${esc(g.name)}</b><div>${g.items.map(esc).join(", ")}</div></div>`).join("")}
    ${profile.certifications?.length ? `<h2>Certifications</h2>${profile.certifications.map((c) => `<div class="cert"><div><b>${esc(c.name)}</b><span>${esc(c.issuer || "")}</span></div><div class="dates">${fmtDate(c.date)}</div></div>`).join("")}` : ""}
    ${edu ? `<h2>Education</h2>${edu}` : ""}
  </aside>
</div>
${later.length || profile.projects?.length ? `<div class="page2">
  ${later.length ? `<h2>Experience <small>continued</small></h2>${later.map(role).join("")}` : ""}
  ${profile.projects?.length ? `<h2>Project index</h2><table><tr><th>Client</th><th>Platform</th><th>Employer</th><th>Work delivered</th></tr>${profile.projects.map((p) => `<tr><td>${esc(p.client)}</td><td>${esc(p.platform)}</td><td>${esc(p.employer)}</td><td>${esc(p.work)}</td></tr>`).join("")}</table>` : ""}
  ${(profile.education?.length || profile.certifications?.length) ? `<h2>Credentials</h2><div class="creds">${[
    ...(profile.education || []).filter((e) => e.status).map((e) => `<div class="cred on"><small>${esc(e.status)}</small><b>${esc(e.degree)}</b><div>${esc(e.institution)} · ${fmtDate(e.start)} – ${fmtDate(e.end)}</div></div>`),
    ...(profile.certifications || []).map((c) => `<div class="cred"><small>Certified</small><b>${esc(c.name)}${c.issuer ? `, ${esc(c.issuer)}` : ""}</b><div>${fmtDate(c.date)}</div></div>`),
    ...(profile.education || []).filter((e) => !e.status).map((e) => `<div class="cred"><small>Degree</small><b>${esc(e.degree)}</b><div>${esc(e.institution)} · ${fmtDate(e.start)} – ${fmtDate(e.end)}</div></div>`),
  ].join("")}</div>` : ""}
</div>` : ""}
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
const countPages = (buf) => (buf.toString("latin1").match(/\/Type\s*\/Page[^s]/g) || []).length;

/**
 * Print, count the real PDF pages, and shrink the text slightly until it fits in
 * `maxPages` (no spill-over page with a few lines on it). Returns the final PDF bytes.
 */
async function printToFit(page, maxPages = 2) {
  let buf;
  for (let zoom = 1; zoom >= 0.8; zoom = +(zoom - 0.03).toFixed(2)) {
    await page.evaluate((z) => (document.body.style.zoom = String(z)), zoom);
    buf = await page.pdf({ format: "A4", printBackground: true, preferCSSPageSize: true });
    if (countPages(buf) <= maxPages) return buf;
  }
  return buf;
}

export async function buildResumePdf(profile, tailored, job) {
  // One folder per job; the file itself gets a recruiter-friendly name.
  const dir = path.join(RESUME_DIR, `${job.platform}-${job.jobId}-${slugify(job.company)}`.slice(0, 100));
  fs.mkdirSync(dir, { recursive: true });
  const fileBase = `${profile.name.trim().replace(/[^A-Za-z0-9]+/g, "-")}-Resume`;
  const htmlPath = path.join(dir, `${fileBase}.html`);
  const pdfPath = path.join(dir, `${fileBase}.pdf`);
  const browser = await getPdfBrowser();
  const page = await browser.newPage();
  // If even slightly smaller text doesn't fit 2 pages, trim the least important content step by step.
  const t = tailored ?? {};
  const exp = t.experience?.length ? t.experience : profile.experience || [];
  const cap = (older, recent) => exp.map((e, i) => ({ ...e, bullets: (e.bullets || []).slice(0, i < 2 ? recent : older) }));
  const variants = [
    [profile, t],
    [profile, { ...t, experience: cap(3, 6) }],
    [profile, { ...t, experience: cap(2, 5) }],
    [{ ...profile, projects: [] }, { ...t, experience: cap(2, 5) }],
  ];
  let buf, html;
  for (const [prof, tt] of variants) {
    html = renderResumeHtml(prof, tt);
    await page.setContent(html, { waitUntil: "networkidle", timeout: 20000 }).catch(() => page.setContent(html, { waitUntil: "load" }));
    await page.evaluate(() => document.fonts?.ready).catch(() => {});
    buf = await printToFit(page);
    if (countPages(buf) <= 2) break;
  }
  fs.writeFileSync(htmlPath, html);
  fs.writeFileSync(pdfPath, buf);
  await page.close();
  return pdfPath;
}

export async function closePdfBrowser() {
  await pdfBrowser?.close();
  pdfBrowser = undefined;
}
