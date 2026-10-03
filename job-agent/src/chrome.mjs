// Finding and starting the agent's own Chrome (dedicated profile in job-agent/.chrome-profile,
// DevTools port open). Used by `npm run chrome` and automatically by the agents when that
// Chrome isn't running.
//
// Port 9222 can be taken by a *different* Chrome: e.g. your everyday Chrome after turning on
// "remote debugging" in chrome://inspect. That one only offers a restricted DevTools connection
// ("Browser context management is not supported"), so the agent then uses port 9333 instead.
import { execFileSync, spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { ROOT, log, sleep } from "./util.mjs";

export const CDP_URL = process.env.CHROME_CDP_URL || "http://127.0.0.1:9222";
const HOST = new URL(CDP_URL).hostname;
const PORTS = [...new Set([new URL(CDP_URL).port || "9222", "9333"])];
const PROFILE_DIR = path.join(ROOT, ".chrome-profile");
const urlFor = (port) => `http://${HOST}:${port}`;

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

async function isUp(url) {
  try {
    return (await fetch(`${url}/json/version`, { signal: AbortSignal.timeout(3000) })).ok;
  } catch {
    return false;
  }
}

export const chromeIsUp = () => isUp(CDP_URL);

/** Main processes of the agent's own Chrome (found by its profile folder), with their DevTools port. */
function agentChromes() {
  if (os.platform() === "win32") return [];
  try {
    return execFileSync("ps", ["-axww", "-o", "pid=,command="], { encoding: "utf8" })
      .split("\n")
      .filter((l) => l.includes(`--user-data-dir=${PROFILE_DIR}`) && !l.includes("--type="))
      .map((l) => ({ pid: Number(l.trim().split(/\s+/)[0]), port: l.match(/--remote-debugging-port=(\d+)/)?.[1] || null }))
      .filter((p) => p.pid && p.pid !== process.pid);
  } catch {
    return [];
  }
}

/** Quit the agent's own Chrome (never any other Chrome) and wait until it's gone. */
async function quitAgentChrome() {
  const procs = agentChromes();
  for (const p of procs) try { process.kill(p.pid, "SIGTERM"); } catch {}
  for (let i = 0; i < 20 && agentChromes().length; i++) await sleep(500);
  for (const p of agentChromes()) try { process.kill(p.pid, "SIGKILL"); } catch {}
  await sleep(1000);
}

const DEFAULT_URLS = ["https://www.linkedin.com/jobs/", "https://www.naukri.com/mnjuser/homepage", "https://app.alignerr.com/home"];

async function startOn(port, urls = DEFAULT_URLS) {
  const exe = findChrome();
  if (!exe) throw new Error("Chrome not found. Set CHROME_PATH in job-agent/.env to Chrome's executable.");
  // The agent's Chrome is open but without a usable DevTools port: a second launch would just
  // hand over to it, so close it first (only that Chrome, recognised by its own profile folder).
  if (agentChromes().length) await quitAgentChrome();
  const child = spawn(exe, [`--remote-debugging-port=${port}`, `--user-data-dir=${PROFILE_DIR}`, "--no-first-run", "--no-default-browser-check", ...(process.env.CHROME_ARGS ? process.env.CHROME_ARGS.split(" ") : []), ...urls], { detached: true, stdio: "ignore" });
  child.unref();
  for (let i = 0; i < 40; i++) {
    await sleep(500);
    if (await isUp(urlFor(port))) return true;
  }
  return false;
}

const RESTRICTED = /context management is not supported/i;

/**
 * Connects to the agent's Chrome, starting (or restarting) it when needed.
 * connectFn(url) does the actual Playwright connect and returns its result.
 */
export async function ensureChrome(connectFn) {
  const tried = [];
  // 1) A Chrome that's already up on one of our ports.
  for (const port of PORTS) {
    const url = urlFor(port);
    if (!(await isUp(url))) continue;
    try {
      return { url, ...(await connectFn(url)) };
    } catch (e) {
      const msg = e.message.split("\n")[0];
      tried.push(`${port}: ${msg}`);
      if (!RESTRICTED.test(msg)) continue;
      const ours = agentChromes().some((p) => p.port === port);
      if (ours) {
        log("warn", `The agent's Chrome on port ${port} isn't accepting the connection; restarting it (your logins are kept)…`);
        if (await startOn(port).catch(() => false)) {
          await sleep(4000);
          try {
            return { url, ...(await connectFn(url)) };
          } catch (e2) {
            tried.push(`${port} after restart: ${e2.message.split("\n")[0]}`);
          }
        }
      } else log("warn", `Port ${port} is used by another Chrome (probably your normal Chrome with remote debugging turned on), not the agent's. Using a different port for the agent's Chrome.`);
    }
  }
  // 2) Start the agent's Chrome on the first free port.
  for (const port of PORTS) {
    const url = urlFor(port);
    if (await isUp(url)) continue;
    log("warn", "The agent's Chrome isn't running — starting it…");
    if (!(await startOn(port).catch((e) => (tried.push(`${port}: ${e.message}`), null)))) {
      tried.push(`${port}: Chrome didn't open its DevTools port`);
      continue;
    }
    log("ok", "Chrome started. (If LinkedIn/Naukri/Alignerr ask you to log in, log in once in that window.)");
    await sleep(4000);
    try {
      return { url, ...(await connectFn(url)) };
    } catch (e) {
      tried.push(`${port}: ${e.message.split("\n")[0]}`);
    }
  }
  throw new Error(tried.join(" · ") || "no Chrome found");
}

/** For `npm run chrome`: start the agent's Chrome unless it's already reachable. Returns the URL or null. */
export async function launchChrome(urls = DEFAULT_URLS) {
  for (const port of PORTS) {
    if (!(await isUp(urlFor(port)))) continue;
    if (agentChromes().some((p) => p.port === port) || os.platform() === "win32") return urlFor(port);
  }
  for (const port of PORTS) if (!(await isUp(urlFor(port))) && (await startOn(port, urls))) return urlFor(port);
  return null;
}
