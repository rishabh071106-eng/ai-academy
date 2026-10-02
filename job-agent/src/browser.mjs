import { chromium } from "playwright-core";
import { log } from "./util.mjs";

/** Attach to the already-running, already-logged-in Chrome. */
export async function connect() {
  const url = process.env.CHROME_CDP_URL || "http://127.0.0.1:9222";
  try {
    const browser = await chromium.connectOverCDP(url);
    const context = browser.contexts()[0];
    if (!context) throw new Error("No browser context");
    log("ok", `Connected to Chrome at ${url}`);
    return { browser, context };
  } catch (e) {
    throw new Error(`Could not reach Chrome at ${url}. Start it with \`npm run chrome\` (and keep it open). (${e.message})`);
  }
}

/** First visible element out of several candidate selectors, or null. */
export async function firstVisible(scope, selectors, timeout = 0) {
  const deadline = Date.now() + timeout;
  do {
    for (const sel of selectors) {
      const loc = scope.locator(sel);
      const n = await loc.count().catch(() => 0);
      for (let i = 0; i < n; i++) {
        const item = loc.nth(i);
        if (await item.isVisible().catch(() => false)) return item;
      }
    }
    if (Date.now() < deadline) await new Promise((r) => setTimeout(r, 300));
  } while (Date.now() < deadline);
  return null;
}

export async function textOf(scope, selectors) {
  const el = await firstVisible(scope, selectors);
  return el ? (await el.innerText().catch(() => "")).trim() : "";
}
