// npm run inspect               → captures the page currently shown in the agent's Chrome
// npm run inspect -- <url>      → opens <url> first
// Saves a screenshot and a text map of the page (buttons, links, fields) to data/debug/inspect/
// so a stuck site can be diagnosed without guessing.
import fs from "node:fs";
import path from "node:path";
import { connect } from "./browser.mjs";
import { snapshot } from "./navigator.mjs";
import { DATA_DIR, log } from "./util.mjs";

const url = process.argv[2];
const { context } = await connect();
const pages = context.pages().filter((p) => !p.url().startsWith("chrome") && !p.url().startsWith("about:") && !p.url().includes("localhost:"));
let page = pages.at(-1);
if (url || !page) {
  page = await context.newPage();
  await page.goto(url || "https://app.alignerr.com/home", { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
}
await page.bringToFront().catch(() => {});
await new Promise((r) => setTimeout(r, 1500));
const dir = path.join(DATA_DIR, "debug", "inspect");
fs.mkdirSync(dir, { recursive: true });
const stamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
const host = new URL(page.url()).hostname.replace(/^www\./, "");
const png = path.join(dir, `${host}-${stamp}.png`);
const txt = path.join(dir, `${host}-${stamp}.txt`);
await page.screenshot({ path: png, fullPage: true });
const s = await snapshot(page);
// Contact details are masked so the file is safe to share.
const mask = (t) => String(t).replace(/[\w.+-]+@[\w-]+\.[\w.]+/g, "<email>").replace(/\+?\d[\d\s-]{8,}\d/g, "<phone>");
fs.writeFileSync(txt, mask([
  `URL: ${s.url}`, `TITLE: ${s.title}`, `HEADINGS: ${s.headings.join(" | ")}`, "", "ELEMENTS:",
  ...s.elements.map((e) => `${e.id} ${e.tag}${e.role ? `[${e.role}]` : ""}${e.type ? `(${e.type})` : ""}${e.disabled ? " disabled" : ""} "${e.text || e.label}"${e.label && e.text ? ` label="${e.label}"` : ""}${e.href ? ` href=${e.href}` : ""}`),
  "", "TEXT:", s.text,
].join("\n")));
log("ok", `Saved:\n  ${png}\n  ${txt}\nSend these two files to Claude (the assistant that built this) to get the site fixed.`);
process.exit(0);
