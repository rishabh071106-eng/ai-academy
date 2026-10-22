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

/**
 * Brings her profile on `site` up to date. Returns { status: "updated" | "needs_attention", note }.
 * `home` = the site's home page; `profileUrl` (optional) = a direct link to her profile/resume page.
 */
export async function updateSiteProfile(page, { key, site, home, profileUrl, profile, resumePath, baseResume, isLoggedIn, mode = "review" }) {
  const resumeName = resumePath ? path.basename(resumePath) : "";
  log("info", `\n[${key}] Updating her ${site} profile from the resume…`);
  await page.goto(profileUrl || home, { waitUntil: "domcontentloaded", timeout: 30000 }).catch(() => {});
  if (!(await ensureAccount(page, site, { isLoggedIn, home }))) return { status: "needs_attention", note: `${site}: couldn't log in to update the profile` };
  if (profileUrl) await page.goto(profileUrl, { waitUntil: "domcontentloaded", timeout: 30000 }).catch(() => {});
  const r = await navigate(page, {
    goal: `Bring her ${site} profile fully up to date so it matches her resume below, section by section. Open My profile / Profile / Resume / Edit profile. For each section (headline or title, summary/about, work experience, skills, education, certifications, contact details, location, notice period, current and expected salary, resume file): open its Edit, replace outdated text with the resume's wording, add anything missing (each employer with role, dates, location and 2–4 bullet points; every skill listed), keep what already matches, and Save. Upload the resume PDF where the site keeps a resume (upload_resume), replacing the old one. Mark her as actively looking / open to work if the site has such a setting. Dismiss tips and pop-ups.
THE RESUME FILE MATTERS MOST: the site must end up with her NEW resume${resumeName ? ` ("${resumeName}", uploaded today)` : ""} as the one and only / default resume. Delete or replace older copies the site still lists (old file names or older upload dates) so applications can't pick an old one. FINAL CHECK before finishing: open the resume section again and confirm the file shown is the new one (today's upload); if it isn't, upload it again.
When every section is saved and the final check passed, use done with status "applied" (meaning: profile updated) and list in message what you changed and the resume file the site now shows.

HER RESUME:
${resumeText(profile)}`,
    rules: `${GOOGLE_RULES(profile.email)}
- Edit only her own profile. Never delete an employer, degree or skill that is also on the resume; never add anything that isn't on it.
- Dates: use the resume's months and years exactly; "present" means she still works there.
- A section without an edit control is skipped. A section that needs a document (ID proof, photo) is skipped.
- If a save fails because a required field is empty, fill it from the resume and save again.
- need_user only for a CAPTCHA, an SMS code, or a question the resume can't answer; the person will do it on screen and press Continue.`,
    profile,
    resumePath,
    mode,
    // In a jobs run the person gets 10 minutes to do a code / CAPTCHA on screen; on demand it waits.
    helpTimeoutMs: mode === "auto" ? Number(loadConfig().profileSync?.helpMinutes ?? 10) * 60000 : 0,
    maxSteps: Number(loadConfig().profileSync?.maxSteps ?? 70),
  }).catch((e) => ({ status: "needs_attention", note: e.message }));
  if (r.status === "applied") {
    markUpdated(key, r.note, resumePath, baseResume);
    log("ok", `[${key}] Profile updated: ${String(r.note || "").slice(0, 200)}`);
    return { status: "updated", note: r.note };
  }
  log("warn", `[${key}] Profile update not finished: ${r.note}`);
  return { status: "needs_attention", note: r.note };
}
