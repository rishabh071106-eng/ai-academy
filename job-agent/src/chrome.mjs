// Finding and starting the agent's own Chrome (dedicated profile in job-agent/.chrome-profile,
// DevTools port open). Used by `npm run chrome` and automatically by the agents when that
// Chrome isn't running.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { ROOT, sleep } from "./util.mjs";

export const CDP_URL = process.env.CHROME_CDP_URL || "http://127.0.0.1:9222";
const port = new URL(CDP_URL).port || "9222";

export function findChrome() {
  const candidates = {
    darwin: ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", path.join(os.homedir(), "Applications/Google Chrome.app/Contents/MacOS/Google Chrome")],
    win32: [
      path.join(process.env["PROGRAMFILES"] ?? "C:\\Program Files", "Google\\Chrome\\Application\\chrome.exe"),
      path.join(process.env["PROGRAMFILES(X86)"] ?? "C:\\Program Files (x86)", "Google\\Chrome\\Application\\chrome.exe"),
      path.join(process.env.LOCALAPPDATA ?? "", "Google\\Chrome\\Application\\chrome.exe"),
    ],
    linux: ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser"],
  }[os.platform()] ?? [];
  return process.env.CHROME_PATH || candidates.find((p) => fs.existsSync(p)) || null;
}

export async function chromeIsUp() {
  try {
    const r = await fetch(`${CDP_URL}/json/version`);
    return r.ok;
  } catch {
    return false;
  }
}

/** Start the agent's Chrome (if not already up) and wait until it accepts connections. */
export async function launchChrome(urls = ["https://www.linkedin.com/jobs/", "https://www.naukri.com/mnjuser/homepage", "https://app.alignerr.com/home"]) {
  if (await chromeIsUp()) return true;
  const exe = findChrome();
  if (!exe) throw new Error("Chrome not found. Set CHROME_PATH in job-agent/.env to Chrome's executable.");
  const child = spawn(exe, [`--remote-debugging-port=${port}`, `--user-data-dir=${path.join(ROOT, ".chrome-profile")}`, "--no-first-run", "--no-default-browser-check", ...urls], { detached: true, stdio: "ignore" });
  child.unref();
  for (let i = 0; i < 40; i++) {
    await sleep(500);
    if (await chromeIsUp()) return true;
  }
  return false;
}
