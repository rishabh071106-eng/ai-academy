// Keeps profile.json in step with her latest resume PDF (default: newest
// ~/Downloads/Aishwarya-Sharma-Resume*.pdf). Her contact details, screening answers and
// skill years are kept; everything on the resume (summary, roles, skills, projects…) is
// re-read from the PDF whenever the file changes.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { extractProfile } from "./llm.mjs";
import { log, readJson, ROOT, sleep } from "./util.mjs";

const PROFILE = path.join(ROOT, "profile.json");

/** Newest file matching a pattern like "~/Downloads/Aishwarya-Sharma-Resume*.pdf". */
export function findBaseResume(pattern) {
  if (!pattern) return null;
  const full = pattern.replace(/^~(?=\/|$)/, os.homedir());
  const dir = path.dirname(full);
  const re = new RegExp(`^${path.basename(full).replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*")}$`, "i");
  let files = [];
  try {
    files = fs.readdirSync(dir).filter((f) => re.test(f)).map((f) => path.join(dir, f));
  } catch {
    return null;
  }
  return files.map((f) => ({ path: f, mtimeMs: fs.statSync(f).mtimeMs })).sort((a, b) => b.mtimeMs - a.mtimeMs)[0] ?? null;
}

async function withLock(fn) {
  const lock = PROFILE + ".lock";
  for (let i = 0; ; i++) {
    try {
      fs.closeSync(fs.openSync(lock, "wx"));
      break;
    } catch {
      try {
        if (Date.now() - fs.statSync(lock).mtimeMs > 180000) fs.rmSync(lock, { force: true });
      } catch {}
      if (i > 600) throw new Error("profile.json is locked");
      await sleep(500); // the other agent is updating the profile
    }
  }
  try {
    return await fn();
  } finally {
    fs.rmSync(lock, { force: true });
  }
}

/** Rebuild the resume part of profile.json from a PDF, keeping her answers and contact details. */
export async function importResume(pdfPath, { reason = "" } = {}) {
  return withLock(async () => {
    const current = readJson(PROFILE, readJson(path.join(ROOT, "profile.example.json")));
    log("info", `Reading ${path.basename(pdfPath)}${reason ? ` (${reason})` : ""}…`);
    const x = await extractProfile(fs.readFileSync(pdfPath).toString("base64"));
    if (fs.existsSync(PROFILE)) fs.copyFileSync(PROFILE, PROFILE.replace(/\.json$/, `.backup-${Date.now()}.json`));
    const keep = (a, b) => (a && String(a).trim() ? a : b);
    const next = {
      ...current,
      ...x,
      // Contact details: prefer the resume, fall back to what we had.
      email: keep(x.email, current.email),
      phone: keep(String(x.phone || "").replace(/\D/g, "").replace(/^91(?=\d{10}$)/, ""), current.phone),
      phoneCountryCode: current.phoneCountryCode || "+91",
      city: keep(x.city, current.city),
      linkedinUrl: keep(x.linkedinUrl && !/^https?:/.test(x.linkedinUrl) ? `https://www.${x.linkedinUrl.replace(/^www\./, "")}` : x.linkedinUrl, current.linkedinUrl),
      skillYears: current.skillYears ?? {},
      applicationAnswers: current.applicationAnswers ?? {},
      sourceResume: { path: pdfPath, name: path.basename(pdfPath), mtimeMs: fs.statSync(pdfPath).mtimeMs, importedAt: new Date().toISOString() },
    };
    fs.writeFileSync(PROFILE, JSON.stringify(next, null, 2));
    log("ok", `Profile updated from ${path.basename(pdfPath)}: ${next.experience?.length ?? 0} roles, ${next.skillGroups?.length ?? 0} skill groups, ${next.projects?.length ?? 0} projects`);
    return next;
  });
}

/** Called at the start of every run: re-import if the resume in Downloads is new or changed. */
export async function syncProfile(config) {
  const base = findBaseResume(config.baseResume);
  if (!base) {
    log("warn", `No resume matching ${config.baseResume} found; using profile.json as is`);
    return null;
  }
  const cur = readJson(PROFILE, {});
  if (cur.sourceResume?.path === base.path && cur.sourceResume?.mtimeMs === base.mtimeMs) {
    log("dim", `Using resume: ${path.basename(base.path)}`);
    return base;
  }
  // Another agent may be importing right now; wait for it and re-check.
  await importResume(base.path, { reason: cur.sourceResume ? "new version found" : "first time" }).catch((e) => log("err", `Couldn't read the resume: ${e.message}`));
  return base;
}
