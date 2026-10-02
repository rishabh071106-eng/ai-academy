// npm run import-resume                      → newest resume matching config.baseResume
// npm run import-resume -- path/to/resume.pdf → that file
// Rebuilds the resume part of profile.json; her screening answers and contact details are kept.
import fs from "node:fs";
import { findBaseResume, importResume } from "./profile-sync.mjs";
import { loadConfig, log } from "./util.mjs";

const file = process.argv[2] || findBaseResume(loadConfig().baseResume)?.path;
if (!file || !fs.existsSync(file)) {
  log("err", "No resume found. Usage: npm run import-resume -- path/to/resume.pdf");
  process.exit(1);
}
await importResume(file);
