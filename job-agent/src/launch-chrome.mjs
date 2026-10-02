// Starts Chrome with the DevTools port open so the agent can drive it.
// Chrome (v136+) refuses remote debugging on your *default* profile, so this uses a
// dedicated profile in job-agent/.chrome-profile. Log in to LinkedIn and Naukri in
// that window once; the logins persist for every later run.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { ROOT, log } from "./util.mjs";

const port = new URL(process.env.CHROME_CDP_URL || "http://127.0.0.1:9222").port || "9222";
const candidates = {
  darwin: ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
  win32: [
    path.join(process.env["PROGRAMFILES"] ?? "C:\\Program Files", "Google\\Chrome\\Application\\chrome.exe"),
    path.join(process.env["PROGRAMFILES(X86)"] ?? "C:\\Program Files (x86)", "Google\\Chrome\\Application\\chrome.exe"),
    path.join(process.env.LOCALAPPDATA ?? "", "Google\\Chrome\\Application\\chrome.exe"),
  ],
  linux: ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser"],
}[os.platform()] ?? [];

const exe = process.env.CHROME_PATH || candidates.find((p) => fs.existsSync(p));
if (!exe) {
  log("err", "Chrome not found. Set CHROME_PATH in job-agent/.env to chrome's executable.");
  process.exit(1);
}

const profileDir = path.join(ROOT, ".chrome-profile");
const child = spawn(exe, [
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${profileDir}`,
  "--no-first-run",
  "--no-default-browser-check",
  "https://www.linkedin.com/jobs/",
  "https://www.naukri.com/mnjuser/homepage",
], { detached: true, stdio: "ignore" });
child.unref();

log("ok", `Chrome started with DevTools on port ${port} (profile: .chrome-profile).`);
log("info", "Log in to LinkedIn and Naukri in that window (first time only), then run: npm run agent");
