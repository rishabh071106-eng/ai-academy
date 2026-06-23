# Learn AI Like a Kid 📖

A print-ready, fully-illustrated children's book that teaches **artificial
intelligence and its real algorithms** to readers ages **10–14** — through the
animal students of *Whisker Woods Academy*. Every chapter is a "class": a story,
a hand-drawn diagram, the honest explanation of a real algorithm, a hands-on
activity, and the grown-up vocabulary.

It is designed to be exported to PDF and sold on **Amazon KDP** (6 × 9 in trade
paperback), and it also reads beautifully in any web browser.

## What's inside

- **21 classes** across 5 parts — from *What Is AI?* to decision trees, nearest
  neighbors, clustering, regression, overfitting, neural networks, training,
  computer vision, sequences, language models, attention, reinforcement learning,
  search/pathfinding, recommendations, generative AI, bias & fairness, AI safety,
  and a "become a maker" finale.
- **~32,000 words**, **56 hand-drawn SVG illustrations** (cute characters + real
  concept diagrams), an auto-generated **Table of Contents**, **The AI Dictionary**
  (glossary), **The Maker Lab** (12 projects), and a **For Grown-Ups & Teachers** note.

## How it's built

Each page lives as a small HTML fragment in `parts/`. A build script stitches them
together (in the order set by `manifest.json`), inlines the styling from `theme.css`,
auto-builds the Table of Contents, and writes one **self-contained** file:

```
book/
├─ manifest.json     ← page order + part names
├─ theme.css         ← the house style (screen + 6×9 print CSS)
├─ build.mjs         ← assembles everything
├─ AUTHORING.md      ← the style guide every chapter follows
├─ parts/            ← cover, front matter, ch01–ch21, back matter (one file each)
└─ dist/
   └─ learn-ai-like-a-kid.html   ← the finished, portable book
```

### Build it

```bash
node book/build.mjs
```

### Read it on screen

Open `book/dist/learn-ai-like-a-kid.html` in any browser (or run the repo's
`npm run dev` server and visit `/book/dist/learn-ai-like-a-kid.html`).

## Export the Amazon KDP interior (PDF)

1. Open `book/dist/learn-ai-like-a-kid.html` in **Google Chrome**.
2. **File → Print** (or click the *Print / Save PDF* button at the top).
3. Settings:
   - **Destination:** Save as PDF
   - **Paper size:** the page CSS is already set to **6 × 9 in** — choose that size,
     or a custom 6×9 if your print dialog supports it.
   - **Margins:** Default (the print CSS sets KDP-friendly margins).
   - **Background graphics:** ✅ **ON** (so the colors and boxes print).
4. Save. That PDF is your **book interior**, ready to upload to KDP.

> The on-screen toolbar and the "desk" background are screen-only and are
> automatically hidden when printing.

### Notes for publishing

- The first page is a printable **cover mockup**. Amazon KDP builds the real
  cover separately (with spine + back) using their Cover Creator or a template —
  use that page as your art direction.
- Final page count depends on your PDF settings; at 6×9 with these margins the
  book runs to a substantial paperback. Check KDP's live page count after upload.
- Want to add or reorder classes? Drop a new `chNN.html` in `parts/`, add it to
  `manifest.json`, and re-run the build. Follow `AUTHORING.md` to keep the style.

## Editing a chapter

Open the matching file in `parts/` (e.g. `parts/ch09.html`), edit the HTML, and
re-run `node book/build.mjs`. The Table of Contents updates itself from each
chapter's `data-toc-*` attributes.
