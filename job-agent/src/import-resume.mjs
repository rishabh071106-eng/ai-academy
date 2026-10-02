// npm run import-resume -- path/to/resume.pdf
// Builds profile.json from a resume PDF with Claude. Review it afterwards and fill applicationAnswers.
import fs from "node:fs";
import path from "node:path";
import { extractProfile } from "./llm.mjs";
import { ROOT, log, readJson } from "./util.mjs";

const file = process.argv[2];
if (!file || !fs.existsSync(file)) {
  log("err", "Usage: npm run import-resume -- path/to/resume.pdf");
  process.exit(1);
}
const out = path.join(ROOT, "profile.json");
if (fs.existsSync(out)) fs.copyFileSync(out, out.replace(/\.json$/, `.backup-${Date.now()}.json`));

const extracted = await extractProfile(fs.readFileSync(file).toString("base64"));
const template = readJson(path.join(ROOT, "profile.example.json"));
const profile = { ...template, ...extracted, phoneCountryCode: "+91", skillYears: {}, applicationAnswers: template.applicationAnswers };
fs.writeFileSync(out, JSON.stringify(profile, null, 2));
log("ok", `Wrote profile.json for ${profile.name}. Now fill skillYears and the TODOs in applicationAnswers.`);
