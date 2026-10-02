import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const DATA_DIR = path.join(ROOT, "data");
export const RESUME_DIR = path.join(DATA_DIR, "resumes");
fs.mkdirSync(RESUME_DIR, { recursive: true });

// Minimal .env loader so there is no extra dependency.
const envFile = path.join(ROOT, ".env");
if (fs.existsSync(envFile)) {
  for (const line of fs.readFileSync(envFile, "utf8").split("\n")) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
    if (m && !process.env[m[1]] && m[2] !== "") process.env[m[1]] = m[2].replace(/^["']|["']$/g, "");
  }
}

export function readJson(file, fallback) {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    if (fallback !== undefined) return fallback;
    throw new Error(`Could not read ${path.relative(ROOT, file)}`);
  }
}

export function loadConfig() {
  return readJson(path.join(ROOT, "config.json"));
}

export function loadProfile() {
  const file = path.join(ROOT, "profile.json");
  if (!fs.existsSync(file)) {
    throw new Error("profile.json not found. Run `npm run import-resume -- <resume.pdf>` or copy profile.example.json to profile.json.");
  }
  return readJson(file);
}

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
export const randomBetween = (min, max) => Math.round(min + Math.random() * (max - min));
export const humanPause = (min = 800, max = 2200) => sleep(randomBetween(min, max));

export function slugify(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 60);
}

const COLORS = { info: 36, ok: 32, warn: 33, err: 31, dim: 90 };
export function log(kind, ...msg) {
  const c = COLORS[kind] ?? 0;
  const t = new Date().toLocaleTimeString();
  console.log(`\x1b[90m${t}\x1b[0m \x1b[${c}m${msg.join(" ")}\x1b[0m`);
}

export async function ask(question) {
  const readline = await import("node:readline/promises");
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  try {
    return (await rl.question(`\x1b[35m? ${question}\x1b[0m `)).trim();
  } finally {
    rl.close();
  }
}
