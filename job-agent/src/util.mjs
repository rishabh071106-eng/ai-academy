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

// ---- "Skip this job" from the dashboard. The agent marks the job it is
// working on as active; a skip request then ends that job at the next pause (every wait in the
// agent goes through sleep()), and any question waiting for an answer is closed at once.
export const jobControl = { active: false, skip: false };
export class SkipJob extends Error {
  constructor() {
    super("Skipped by you");
    this.name = "SkipJob";
  }
}
export const isSkip = (e) => e?.name === "SkipJob";
export function checkSkip() {
  if (jobControl.active && jobControl.skip) throw new SkipJob();
}
export const sleep = async (ms) => {
  await new Promise((r) => setTimeout(r, ms));
  checkSkip();
};

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

let askSeq = 0;

/**
 * Ask the user something. When the agent was started from the dashboard it has an IPC
 * channel to the server, so the question shows up there as buttons; otherwise it's asked
 * in the terminal. `choices` = [{ label, value }].
 */
export async function ask(question, choices, { timeoutMs = 0, timeoutAnswer = "s" } = {}) {
  if (process.send) {
    const id = ++askSeq;
    process.send({ type: "ask", id, question, choices, timeoutMs });
    return new Promise((resolve) => {
      let timer;
      const onMsg = (m) => {
        if (m?.type === "answer" && m.id === id) {
          clearTimeout(timer);
          process.off("message", onMsg);
          resolve(String(m.answer ?? "").trim());
        }
        // "Skip this job" while a question is open: answer it with No / Skip right away.
        if (m?.type === "skip") {
          clearTimeout(timer);
          process.off("message", onMsg);
          process.send({ type: "ask-timeout", id, skipped: true });
          resolve(choices?.some((c) => c.value === "n") ? "n" : "s");
        }
      };
      process.on("message", onMsg);
      // Unattended runs: if nobody answers in time, take the default (normally "skip") and go on.
      if (timeoutMs > 0)
        timer = setTimeout(() => {
          process.off("message", onMsg);
          process.send({ type: "ask-timeout", id });
          log("warn", `   no answer within ${timeoutMs >= 60000 ? `${Math.round(timeoutMs / 60000)} min` : `${Math.round(timeoutMs / 1000)} s`} — moving on`);
          resolve(timeoutAnswer);
        }, timeoutMs);
    });
  }
  const readline = await import("node:readline/promises");
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const hint = choices?.length ? ` [${choices.map((c) => `${c.value || "Enter"}=${c.label}`).join(", ")}]` : "";
  try {
    return (await rl.question(`\x1b[35m? ${question}${hint}\x1b[0m `)).trim();
  } finally {
    rl.close();
  }
}

/** Yes/no question. Defaults to yes on a bare Enter in the terminal. */
export async function confirm(question) {
  const r = await ask(question, [{ label: "Yes", value: "y" }, { label: "No", value: "n" }]);
  return !/^n/i.test(r);
}

/** Pause until the user has done something by hand in Chrome. Returns false if they chose to skip. */
export async function waitForUser(question, { allowSkip = true } = {}) {
  const choices = [{ label: "Done, continue", value: "" }];
  if (allowSkip) choices.push({ label: "Skip this job", value: "s" });
  const r = await ask(question, choices);
  return r.toLowerCase() !== "s";
}

/**
 * Claude API problems no retry can fix (no credit, bad key). The agent stops with a clear
 * message and exit code 3 so the dashboard shows it and does not auto-restart.
 */
export function stopIfFatalApiError(e) {
  const msg = String(e?.message ?? e);
  let why = null;
  if (/credit balance is too low|billing|purchase credits/i.test(msg)) why = "Your Anthropic API credit has run out. Add credit at console.anthropic.com → Settings → Billing, then press Start again.";
  else if (/invalid x-api-key|authentication_error|401/i.test(msg)) why = "The Claude API key in job-agent/.env is not valid. Put a working key there, then press Start again.";
  else if (/permission_error|403/i.test(msg) && /api/i.test(msg)) why = "The Claude API key doesn't have access to this model. Check the key's workspace in the Anthropic Console.";
  if (!why) return;
  log("err", `\n■ STOPPED: ${why}`);
  process.exit(3);
}

/**
 * Unattended mode ("auto"): ask for help on the dashboard but don't wait
 * forever. Returns null when there is no dashboard to ask, so the caller just skips.
 */
export async function askForHelp(question, choices) {
  const cfg = loadConfig();
  if (!process.send) return null;
  const minutes = Number(cfg.helpTimeoutMinutes ?? 3);
  if (minutes <= 0) return null;
  return ask(question, choices, { timeoutMs: minutes * 60000, timeoutAnswer: "s" });
}
