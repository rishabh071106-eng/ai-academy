# Loan Lifecycle — Interview Prep

A complete, interview-ready field guide to the end-to-end loan lifecycle:
origination → underwriting → pricing → closing & funding → servicing →
delinquency → loss mitigation → charge-off/recovery → payoff. Plus the
money math, key ratios, loan types, U.S. regulation, system-design
considerations, 40+ Q&A, a glossary, and a one-page cheat sheet.

## Files

| File | What it is |
|------|------------|
| `loan-lifecycle-interview-prep.pdf` | **The deliverable** — print-ready PDF. |
| `loan-lifecycle.html` | Source document (self-contained, no external assets). |
| `build-pdf.mjs` | Renders the HTML to PDF via Chromium/Playwright. |

## Rebuild the PDF

```bash
npm install playwright          # if not already available
node interview-prep/loan-lifecycle/build-pdf.mjs
```

The build script prefers the environment's pre-installed Chromium
(`/opt/pw-browsers/...`) and falls back to Playwright's bundled browser.
Edit `loan-lifecycle.html` and re-run to regenerate.

> Educational summary of common U.S. consumer-lending practice — not legal,
> financial, or compliance advice. Specifics vary by product, lender, and
> jurisdiction.
