import { chromium } from "playwright-core";
import { ensureChrome } from "./chrome.mjs";
import { log } from "./util.mjs";

/** Attach to the agent's Chrome, starting or restarting it when needed. */
export async function connect() {
  try {
    const { url, browser, context } = await ensureChrome(async (url) => {
      const browser = await chromium.connectOverCDP(url);
      const context = browser.contexts()[0];
      if (!context) {
        await browser.close().catch(() => {});
        throw new Error("No browser context");
      }
      return { browser, context };
    });
    log("ok", `Connected to Chrome at ${url}`);
    return { browser, context };
  } catch (e) {
    log("err", `\n■ STOPPED: Couldn't connect to the agent's Chrome (${e.message.slice(0, 300)}). Quit Chrome completely (Cmd+Q on every Chrome window), then press Start again — the agent opens its own Chrome.`);
    process.exit(3);
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

/**
 * Layout-independent read of a job page: the tab title plus the visible text of the main
 * area. Claude extracts title/company/description from this when CSS selectors miss.
 */
export async function readPage(page) {
  return page.evaluate(() => {
    const main = document.querySelector("main") || document.body;
    const h1 = document.querySelector("h1")?.innerText?.trim() || "";
    return { docTitle: document.title, h1, pageText: (main.innerText || "").replace(/\n{3,}/g, "\n\n").slice(0, 25000) };
  });
}

const MORE = /see more|show more|read more|view more|show full|see full|view full|full description|…\s*more|\.\.\.\s*more|^more$/i;
// Don't click "Show more jobs", "See more companies", comments, etc.
const NOT_MORE = /jobs|results|companies|people|comments|similar|recommend|insights|premium|salary|reviews|alumni|posts/i;

/**
 * Opens the whole job: scrolls through the page so lazy sections load, then clicks every
 * "See more / Show more / …more" control on the description until the text stops growing.
 * Returns how many expanders it clicked.
 */
export async function expandJob(page, scope = "main") {
  const root = page.locator(scope).first();
  const textLen = () => root.evaluate((el) => el.innerText.length).catch(() => 0);

  // Scroll down in steps (lazy-loaded description / hiring team), then back to the top.
  for (let i = 0; i < 6; i++) {
    await page.mouse.wheel(0, 900).catch(() => {});
    await page.waitForTimeout(350);
  }
  await page.evaluate(() => window.scrollTo(0, 0)).catch(() => {});

  let clicked = 0;
  let before = await textLen();
  for (let round = 0; round < 4; round++) {
    // Tag matching expanders in one pass inside the page (fast, and immune to the DOM changing under us).
    const count = await root.evaluate((el, { more, notMore }) => {
      const MORE = new RegExp(more, "i"), NOT = new RegExp(notMore, "i");
      document.querySelectorAll("[data-ja-more]").forEach((e) => e.removeAttribute("data-ja-more"));
      let k = 0;
      for (const e of el.querySelectorAll("button, a, [role=button], span[class*=more], [aria-expanded=false]")) {
        const label = (e.getAttribute("aria-label") || e.innerText || "").trim();
        if (!label || label.length > 60 || !MORE.test(label) || NOT.test(label)) continue;
        if (!(e.offsetParent || e.getClientRects().length)) continue;
        const href = e.getAttribute("href");
        if (href && !href.startsWith("#") && !href.startsWith("javascript")) continue; // never navigate away
        e.setAttribute("data-ja-more", String(k++));
      }
      return k;
    }, { more: MORE.source, notMore: NOT_MORE.source }).catch(() => 0);

    let thisRound = 0;
    for (let i = 0; i < count; i++) {
      const el = page.locator(`[data-ja-more="${i}"]`);
      if (!(await el.count())) continue;
      await el.scrollIntoViewIfNeeded({ timeout: 1000 }).catch(() => {});
      await el.click({ timeout: 1500 }).then(() => thisRound++).catch(() => {});
      await page.waitForTimeout(500);
    }
    clicked += thisRound;
    const after = await textLen();
    if (!thisRound || after <= before) break;
    before = after;
  }
  return clicked;
}
