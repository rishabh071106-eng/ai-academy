// Rebuilds her standard resume PDF (same design as always) from the newest resume in Downloads
// plus the extraSkills in config.json, and saves it to Downloads so every agent picks it up.
//   npm run build-resume
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { syncProfile } from "./profile-sync.mjs";
import { buildResumePdf, closePdfBrowser } from "./resume.mjs";
import { loadConfig, loadProfile, log } from "./util.mjs";

const config = loadConfig();
await syncProfile(config).catch((e) => log("warn", `Could not re-read the resume in Downloads (${String(e.message).split("\n")[0]}); using profile.json as is`));
const profile = loadProfile();
const extra = Object.values(config.extraSkills ?? {}).flat();
if (extra.length) log("info", `Skills added from config.json: ${extra.join(", ")}`);
const pdf = await buildResumePdf(profile, {}, { platform: "base", jobId: "standard", company: "base" });
await closePdfBrowser();
const dir = path.dirname(String(config.baseResume || "~/Downloads/x").replace(/^~(?=$|\/)/, os.homedir()));
fs.mkdirSync(dir, { recursive: true });
const out = path.join(dir, `${profile.name.trim().replace(/[^A-Za-z0-9]+/g, "-")}-Resume_final.pdf`);
fs.copyFileSync(pdf, out);
log("ok", `Resume saved: ${out}`);
log("dim", "Every agent uses it from its next round; profile updates on the sites upload it. Keep it there.");
process.exit(0);
