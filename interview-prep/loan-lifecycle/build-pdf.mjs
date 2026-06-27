#!/usr/bin/env node
/* ------------------------------------------------------------------
   build-pdf.mjs — renders loan-lifecycle.html to a print-ready PDF
   using the pre-installed Chromium via Playwright.

   Run:  node interview-prep/loan-lifecycle/build-pdf.mjs
   Out:  interview-prep/loan-lifecycle/loan-lifecycle-interview-prep.pdf
   ------------------------------------------------------------------ */
import { chromium } from "playwright";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { stat } from "node:fs/promises";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = join(HERE, "loan-lifecycle.html");
const OUT = join(HERE, "loan-lifecycle-interview-prep.pdf");

// Prefer the environment's pre-installed Chromium; fall back to bundled.
const PINNED = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
const launchOpts = {};
try {
  const { accessSync } = await import("node:fs");
  accessSync(PINNED);
  launchOpts.executablePath = PINNED;
} catch {}
const browser = await chromium.launch(launchOpts);
const page = await browser.newPage();
await page.goto(pathToFileURL(SRC).href, { waitUntil: "networkidle" });
await page.pdf({
  path: OUT,
  format: "Letter",
  printBackground: true,
  margin: { top: "0", bottom: "0", left: "0", right: "0" },
  displayHeaderFooter: true,
  headerTemplate: "<div></div>",
  footerTemplate:
    '<div style="width:100%;font-family:Helvetica,Arial,sans-serif;font-size:8px;color:#8a93a3;padding:0 0.55in;display:flex;justify-content:space-between;">' +
    '<span>The Loan Lifecycle · Interview Prep</span>' +
    '<span class="pageNumber"></span>' +
    "</div>",
});
await browser.close();

const { size } = await stat(OUT);
console.log(`✓ wrote ${OUT}`);
console.log(`  ${(size / 1024).toFixed(0)} KB`);
