# Lending & Pricing, Explained Like a Story

A **beginner-first** companion to the JD-aligned prep pack — written for someone
brand new to banking who wants the concepts taught from zero, in plain English,
as a story.

## What it teaches

- **How a bank makes money** (the deposit→loan→spread idea, in one picture)
- **The whole loan lifecycle as a story** — we follow *Aina*, who buys her first
  apartment, through every stage: apply → credit check → approve & price →
  disburse → repay → (trouble → help → recover) → settle. Every term is defined
  the moment it appears.
- **Risk-based pricing from scratch** — why rates differ, what interest really is,
  the **five-ingredient price stack**, **PD/LGD/EAD** and Expected Loss with real
  worked numbers, and a full **Aina-vs-Ben** comparison showing how a riskier
  borrower pays ~RM 87k more for the same loan.
- **Core banking** in one simple picture, and where a **Product Owner** fits.
- **Maybank & MBB Labs** (researched, mid-2026): mission, T.I.G.E.R. values, the
  current **ROAR30** strategy (RM 10bn on tech/data/AI), and what MBB Labs builds.
- **The face-to-face with the Head of Product Management** — what they care about,
  how to answer (STAR), how to handle "I'm still learning that", likely Q&A,
  questions to ask back, and a night-before checklist.

Friendly callout boxes throughout: **In plain words** (definitions), **Our story**
(narrative), **A quick number** (worked examples), **Say this** (interview lines),
**Why it matters**, and **Watch out**.

## Files

| File | What it is |
|------|------------|
| `lending-and-pricing-explained-simply.pdf` | **The deliverable** — print-ready PDF. |
| `lending-explained-simply.html` | Source (self-contained, inline SVG diagrams). |

## Rebuild

```bash
npm install playwright
# render via the shared pattern (Chromium at /opt/pw-browsers/...)
node interview-prep/maybank-prep/build-pdf.mjs   # (for the JD pack)
```
For this file specifically, render `lending-explained-simply.html` to PDF with
Chromium/Playwright (same approach as `build-pdf.mjs`).

> Numbers in the pricing examples are illustrative and rounded to teach the
> concept. Company facts researched from public sources as of mid-2026 — verify
> current figures. Not legal, financial, or Shariah advice.
