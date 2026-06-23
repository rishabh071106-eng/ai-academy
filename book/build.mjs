#!/usr/bin/env node
/* ------------------------------------------------------------------
   build.mjs — assembles "Learn AI Like a Kid" into one self-contained,
   print-ready HTML file (book/dist/learn-ai-like-a-kid.html).

   - Reads book/manifest.json for the page order + part names.
   - Inlines book/theme.css so the output is a single portable file.
   - Auto-builds the Table of Contents from each chapter's data-* tags.

   Run:  node book/build.mjs
   ------------------------------------------------------------------ */
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(fileURLToPath(import.meta.url));
const PARTS = join(ROOT, "parts");

const read = (p) => readFile(p, "utf8");

const manifest = JSON.parse(await read(join(ROOT, "manifest.json")));
const css = await read(join(ROOT, "theme.css"));

// Pull each ordered fragment off disk.
const fragments = [];
for (const file of manifest.order) {
  try {
    fragments.push({ file, html: await read(join(PARTS, file)) });
  } catch {
    console.warn(`!  missing part (skipped): ${file}`);
  }
}

// Scrape TOC entries from chapter fragments via data attributes.
const tocEntries = [];
const attr = (html, name) => {
  const m = html.match(new RegExp(`data-${name}="([^"]*)"`));
  return m ? m[1] : null;
};
for (const { html } of fragments) {
  const num = attr(html, "toc-num");
  if (!num) continue;
  tocEntries.push({
    num,
    part: attr(html, "toc-part") || "",
    title: attr(html, "toc-title") || "",
    id: attr(html, "id-anchor") || "",
  });
}

// Build the TOC markup grouped by part (parts listed in manifest order).
function buildToc() {
  let rows = "";
  for (const part of manifest.parts) {
    const inPart = tocEntries.filter((e) => e.part === part.key);
    if (!inPart.length) continue;
    rows += `\n      <li class="toc-part">${part.name}</li>`;
    for (const e of inPart) {
      rows += `
      <li class="toc-row">
        <span class="toc-num">${e.num}</span>
        <a class="toc-title" href="#${e.id}">${e.title}</a>
        <span class="toc-dots"></span>
      </li>`;
    }
  }
  return `<section class="page toc" id="toc">
    <h1>Table of Contents</h1>
    <ol>${rows}
    </ol>
  </section>`;
}

const tocHtml = buildToc();

// Stitch the body, swapping the {{TOC}} token for the generated TOC.
const body = fragments
  .map(({ html }) => (html.includes("{{TOC}}") ? html.replace("{{TOC}}", tocHtml) : html))
  .join("\n\n");

const out = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>${manifest.meta.title} — ${manifest.meta.subtitle}</title>
<meta name="description" content="${manifest.meta.description}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Baloo+2:wght@400;500;600;700&family=Bitter:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<style>
${css}
</style>
</head>
<body>
<div class="toolbar no-print">
  <span>📖 <b>${manifest.meta.title}</b> — print or “Save as PDF” at 6×9 in for Amazon KDP</span>
  <button onclick="window.print()">Print / Save PDF</button>
</div>

${body}

<script>
/* tiny niceties for on-screen reading only */
document.addEventListener('keydown', e => { if (e.key === 'p' && (e.metaKey||e.ctrlKey)) { /* let browser print */ } });
</script>
</body>
</html>`;

await mkdir(join(ROOT, "dist"), { recursive: true });
const outPath = join(ROOT, "dist", "learn-ai-like-a-kid.html");
await writeFile(outPath, out, "utf8");

const words = body.replace(/<[^>]+>/g, " ").split(/\s+/).filter(Boolean).length;
console.log(`✓ built ${outPath}`);
console.log(`  ${fragments.length} parts · ${tocEntries.length} classes · ~${words.toLocaleString()} words`);
