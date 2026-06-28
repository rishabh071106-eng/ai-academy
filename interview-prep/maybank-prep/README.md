# Maybank / MBB Labs — Senior Product Owner Interview Prep

A complete, JD-aligned training pack for the **MBB Labs (Maybank's Bengaluru
offshore development centre) Senior Product Owner** role. Built directly from
the job description.

## What it covers

- **Employer & values** — Maybank facts, MBB Labs context, T.I.G.E.R. values
- **The JD, decoded** — every JD requirement mapped to what to know/say + section
- **Core banking** — system of record, modules, modernisation story
- **Lending** — 5 Cs + the end-to-end loan lifecycle (Malaysia / Maybank lens)
- **Origination, collateral & servicing systems** (LOS / collateral / LMS)
- **Deposit management & asset/liability classes** (CASA, cost of funds, ALM, NIM)
- **Rating systems & risk-based pricing** (PD/LGD, scorecards, the pricing chain)
- **Risk management & risk analytics** (Basel, PD·LGD·EAD, ECL/IFRS 9, stress testing)
- **Islamic financing** (Tawarruq, Musharakah Mutanaqisah, profit vs riba)
- **PCI DSS, KYC/AML & data security**
- **System architecture diagrams** — step-by-step method, the shapes, how
  connections work, and a **worked Maybank digital-lending diagram**
- **Functional design → MIS & data visualization** (BRD/FSD, data dictionary)
- **SQL basics** on a banking schema
- **Product ownership, AGILE, JIRA & Confluence**
- **Product lifecycle & implementation**, certifications (CAMS/KYC/FRM)
- **Interview Q&A**, glossary, and a one-page cheat sheet

## Files

| File | What it is |
|------|------------|
| `maybank-senior-product-owner-interview-prep.pdf` | **The deliverable** — print-ready PDF. |
| `maybank-prep.html` | Source document (self-contained, inline SVG diagrams). |
| `build-pdf.mjs` | Renders the HTML to PDF via Chromium/Playwright. |

## Rebuild the PDF

```bash
npm install playwright          # if not already available
node interview-prep/maybank-prep/build-pdf.mjs
```

> Educational interview-prep material. Summarises publicly known concepts and
> common market practice; internal bank systems evolve and are not fully public.
> Not legal, financial, or Shariah advice — verify current BNM / PCI / Basel rules.
