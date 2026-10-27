// Keeps her profile on every job site in line with her resume: headline, summary, experience
// with dates and bullet points, skills, education, certifications, contact details, notice
// period / CTC, and the resume PDF itself. The AI navigator does it section by section, the
// way a person would. Runs once every profileSync.everyDays (7) per site, or on demand from
// the dashboard ("↻ Update profile"). It pauses for a person only on a CAPTCHA / SMS code.
import fs from "node:fs";
import path from "node:path";
import { ensureAccount } from "./login.mjs";
import { GOOGLE_RULES, navigate } from "./navigator.mjs";
import { DATA_DIR, loadConfig, log } from "./util.mjs";

const MEMO = path.join(DATA_DIR, "profile-updates.json");
const readMemo = () => {
  try {
    return JSON.parse(fs.readFileSync(MEMO, "utf8"));
  } catch {
    return {};
  }
};

/** Due when never done, older than everyDays, or the resume file in Downloads has changed since. */
export function profileUpdateDue(site, baseResume) {
  const cfg = loadConfig().profileSync ?? {};
  if (cfg.enabled === false) return false;
  if ((cfg.skip ?? []).includes(site)) return false; // e.g. LinkedIn and Naukri: apply only, never touch the profile
  const days = Number(cfg.everyDays ?? 7);
  const last = readMemo()[site];
  if (!last?.at) return true;
  if (Date.now() - new Date(last.at).getTime() > days * 86400000) return true;
  if (baseResume && (last.resume !== path.basename(baseResume.path) || last.resumeMtime !== baseResume.mtimeMs)) return true;
  return false;
}

/** What the dashboard shows per site: { at, resume, note }. */
export const profileUpdates = () => readMemo();

function markUpdated(site, note, resumePath, baseResume) {
  const memo = readMemo();
  memo[site] = { at: new Date().toISOString(), resume: resumePath ? path.basename(resumePath) : null, resumeMtime: baseResume?.mtimeMs ?? null, note: String(note || "").slice(0, 300) };
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(MEMO, JSON.stringify(memo, null, 2));
}

/** Her resume as plain text for the navigator, so every section can be typed from it. */
function resumeText(profile) {
  const exp = (profile.experience ?? []).map((e) => `• ${e.role} — ${e.company}${e.client ? ` (client: ${e.client})` : ""}, ${e.location || ""}, ${e.start} to ${e.end}\n${(e.bullets ?? []).slice(0, 5).map((b) => `   - ${b}`).join("\n")}`).join("\n");
  const edu = (profile.education ?? []).map((e) => `• ${e.degree}${e.field ? ` in ${e.field}` : ""} — ${e.institution}${e.year || e.end ? ` (${e.year || e.end})` : ""}`).join("\n");
  const cert = (profile.certifications ?? []).map((c) => `• ${typeof c === "string" ? c : `${c.name}${c.issuer ? ` — ${c.issuer}` : ""}${c.year ? ` (${c.year})` : ""}`}`).join("\n");
  const a = profile.applicationAnswers ?? {};
  return `NAME: ${profile.name}
HEADLINE: ${profile.headline}
SUMMARY: ${profile.summary}
TOTAL EXPERIENCE: ${profile.totalExperienceYears} years
LOCATION: ${profile.city}${profile.address ? ` (${profile.address})` : ""}
PHONE: ${profile.phoneCountryCode || "+91"} ${profile.phone} · EMAIL: ${profile.email} · LINKEDIN: ${profile.linkedinUrl || ""}
SKILLS: ${(profile.skills ?? []).join(", ")}
YEARS PER SKILL: ${Object.entries(profile.skillYears ?? {}).map(([k, v]) => `${k} ${v}`).join(", ")}
EXPERIENCE:
${exp}
EDUCATION:
${edu}
CERTIFICATIONS:
${cert || "(none)"}
NOTICE PERIOD: ${a.noticePeriod || a.noticePeriodDays || ""} · CURRENT CTC: ${a.currentCtcLpa ? `${a.currentCtcLpa} LPA` : ""} · EXPECTED CTC: ${a.expectedCtcLpa ? `${a.expectedCtcLpa} LPA` : ""} · OPEN TO RELOCATE: ${a.willingToRelocate || ""}`;
}

const SECTIONS = ["resume file", "headline", "summary", "work experience", "skills", "education", "certifications", "contact details", "job preferences"];

/** The part of the resume one section needs, so each edit gets exactly the right data. */
function sectionData(section, profile, resumeName) {
  const a = profile.applicationAnswers ?? {};
  const tags = loadConfig().skillTags ?? profile.skills ?? [];
  switch (section) {
    case "resume file": return `Upload the NEW resume PDF${resumeName ? ` "${resumeName}"` : ""} with upload_resume, replacing the old one; if the site lists several resumes, make the new one the default and delete older copies.`;
    case "headline": return `Headline / profile title / current designation: "${profile.headline}". Tagline if there is one: "${profile.tagline || ""}". Total experience: ${profile.totalExperienceYears} years.`;
    case "summary": return `Summary / About / Profile summary (replace the old text with exactly this):\n${profile.summary}`;
    case "work experience": return `Every employer must exist with these exact details (add missing ones, fix dates/titles, keep bullets as given):\n${(profile.experience ?? []).map((e) => `• ${e.role} — ${e.company}${e.client ? ` (client: ${e.client})` : ""}, ${e.location || ""}, ${e.start} to ${e.end}\n${(e.bullets ?? []).slice(0, 4).map((b) => `   - ${b}`).join("\n")}`).join("\n")}`;
    case "skills": return `Add ALL of these skills / key skills / tags (one at a time where the field takes tags, choose the site's suggestion when it matches; keep the ones already there):\n${tags.join(", ")}\nYears per skill if asked: ${Object.entries(profile.skillYears ?? {}).map(([k, v]) => `${k} ${v}`).join(", ")}`;
    case "education": return `Education:\n${(profile.education ?? []).map((e) => `• ${e.degree}${e.field ? ` in ${e.field}` : ""} — ${e.institution}${e.year || e.end ? ` (${e.year || e.end})` : ""}`).join("\n") || "(none on the resume: skip)"}`;
    case "certifications": return `Certifications:\n${(profile.certifications ?? []).map((c) => `• ${typeof c === "string" ? c : `${c.name}${c.issuer ? ` — ${c.issuer}` : ""}${c.year ? ` (${c.year})` : ""}`}`).join("\n") || "(none on the resume: skip)"}`;
    case "contact details": return `Name ${profile.name} · phone ${profile.phoneCountryCode || "+91"} ${profile.phone} · email ${profile.email} · location ${profile.city}${profile.address ? ` (${profile.address})` : ""} · LinkedIn ${profile.linkedinUrl || ""}. Gender: ${a.gender || ""}.`;
    case "job preferences": return `Notice period: ${a.noticePeriod || a.noticePeriodDays || ""} · current CTC: ${a.currentCtcLpa ? `${a.currentCtcLpa} LPA (₹${a.currentCtcInr || ""})` : ""} · expected CTC: ${a.expectedCtcLpa ? `${a.expectedCtcLpa} LPA (₹${a.expectedCtcInr || ""})` : ""} · open to relocate: ${a.willingToRelocate || ""} · preferred location: ${profile.city} · job type: full-time · mark her as actively looking / open to work if the site has it.`;
    default: return "";
  }
}

const parseAssessment = (text) => {
  try {
    const m = String(text || "").match(/\[[\s\S]*\]/);
    const arr = m ? JSON.parse(m[0]) : null;
    return Array.isArray(arr) ? arr : null;
  } catch {
    return null;
  }
};

/**
 * Brings her profile on `site` up to date in three passes, so even a small model stays on track:
 *   1. assess — open the profile, compare every section with the resume, report each as ok / outdated / missing;
 *   2. update — one focused edit per section that isn't ok, with exactly that section's data;
 *   3. verify — the resume file on the site is the new one.
 * Returns { status: "updated" | "needs_attention", note }.
 */
export async function updateSiteProfile(page, { key, site, home, profileUrl, profile, resumePath, baseResume, isLoggedIn, mode = "review" }) {
  const resumeName = resumePath ? path.basename(resumePath) : "";
  const cfg = loadConfig().profileSync ?? {};
  const common = {
    rules: `${GOOGLE_RULES(profile.email)}
- Edit only her own profile. Never delete an employer, degree or skill that is also on the resume; never add anything that isn't on it.
- Dates: use the resume's months and years exactly; "present" means she still works there.
- A section without an edit control is skipped. A section that needs a document (ID proof, photo) is skipped.
- If a save fails because a required field is empty, fill it from the resume and save again.
- need_user only for a CAPTCHA, an SMS code, or a question the resume can't answer; the person will do it on screen and press Continue.`,
    profile,
    resumePath,
    mode,
    helpTimeoutMs: mode === "auto" ? Number(cfg.helpMinutes ?? 10) * 60000 : 0,
  };
  const goProfile = async () => {
    if (profileUrl) await page.goto(profileUrl, { waitUntil: "domcontentloaded", timeout: 30000 }).catch(() => {});
  };
  log("info", `\n[${key}] Updating her ${site} profile from the resume…`);
  await page.goto(profileUrl || home, { waitUntil: "domcontentloaded", timeout: 30000 }).catch(() => {});
  if (!(await ensureAccount(page, site, { isLoggedIn, home }))) return { status: "needs_attention", note: `${site}: couldn't log in to update the profile` };
  await goProfile();

  // 1. Assess.
  log("dim", `   step 1/3: looking at what the ${site} profile has today`);
  const assess = await navigate(page, {
    ...common,
    goal: `Look at her ${site} profile (open My profile / Profile / Resume if needed, scroll through all of it, open sections if they are collapsed) and compare it with her resume below. Do not edit anything yet. When you have seen every section, use done (status "none") with message = a JSON array, one entry per section, exactly: [{"section":"resume file"|"headline"|"summary"|"work experience"|"skills"|"education"|"certifications"|"contact details"|"job preferences","status":"ok"|"outdated"|"missing"|"no-edit","note":"what differs"}]. "ok" only when the section already matches the resume (for the resume file: only if it is "${resumeName}" uploaded today).

HER RESUME:
${resumeText(profile)}`,
    maxSteps: Number(cfg.assessSteps ?? 18),
  }).catch((e) => ({ status: "needs_attention", note: e.message }));
  const report = parseAssessment(assess.note) ?? SECTIONS.map((section) => ({ section, status: "unknown", note: "" }));
  const todo = SECTIONS.filter((sec) => (report.find((r) => r.section === sec)?.status ?? "unknown") !== "ok" && report.find((r) => r.section === sec)?.status !== "no-edit");
  log("dim", `   profile check: ${report.map((r) => `${r.section}=${r.status}`).join(" · ")}`);

  // 2. Update what isn't right, one section at a time.
  const done = [], failed = [];
  for (const section of todo) {
    log("dim", `   step 2/3: updating ${section}`);
    await goProfile();
    const r = await navigate(page, {
      ...common,
      goal: `On her ${site} profile, update ONLY the "${section}" section so it matches the resume, then Save. Open its Edit (pencil / Edit / Add), make the change, save, and confirm the saved section shows the new content. Then use done (status "applied") with message = what you changed. If this site has no such section or it can't be edited, use done (status "not_eligible").

${sectionData(section, profile, resumeName)}`,
      maxSteps: Number(cfg.sectionSteps ?? 25),
    }).catch((e) => ({ status: "needs_attention", note: e.message }));
    if (r.status === "applied") done.push(`${section}: ${String(r.note || "").slice(0, 120)}`);
    else if (r.status === "skipped") done.push(`${section}: not on this site`);
    else failed.push(`${section}: ${String(r.note || "").slice(0, 120)}`);
  }

  // 3. Verify the resume file.
  let resumeOk = true;
  if (resumePath) {
    log("dim", `   step 3/3: checking the resume file on ${site}`);
    await goProfile();
    const v = await navigate(page, {
      ...common,
      goal: `Open the resume / CV section of her ${site} profile and check which file it shows. If it is "${resumeName}" (uploaded today), use done (status "applied") with message = the file name and date shown. If it is an older file or missing, upload "${resumeName}" with upload_resume, make it the default, remove older copies if the site lists them, then re-check and use done (status "applied"). If the site has no resume section, use done (status "not_eligible").`,
      maxSteps: 15,
    }).catch((e) => ({ status: "needs_attention", note: e.message }));
    resumeOk = v.status === "applied" || v.status === "skipped";
    (resumeOk ? done : failed).push(`resume file: ${String(v.note || "").slice(0, 120)}`);
  }

  const note = `${done.join(" · ")}${failed.length ? ` · NOT DONE → ${failed.join(" · ")}` : ""}`;
  if (!failed.length || (resumeOk && failed.length <= 2)) {
    markUpdated(key, note, resumePath, baseResume);
    log("ok", `[${key}] Profile updated: ${note.slice(0, 300)}`);
    return { status: "updated", note };
  }
  log("warn", `[${key}] Profile update not finished: ${note.slice(0, 300)}`);
  return { status: "needs_attention", note };
}
