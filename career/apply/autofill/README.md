# Auto-apply robot — run on your laptop

The cloud environment where Claude runs **cannot reach job sites** (the network is
firewalled — verified: connections to Greenhouse/Lever/careers sites don't even open),
and Workday/Greenhouse gate submission behind email OTPs, CAPTCHAs, and an
"I certify this is true" attestation that only the candidate may click. This script is
the legitimate version of "automated apply": **it does all the typing, you do the clicks
that must be yours.**

## One-time setup (5 minutes)

```bash
git clone -b claude/job-search-applications-hd2yno https://github.com/rishabh071106-eng/ai-academy.git
cd ai-academy/career/apply/autofill
npm init -y && npm i playwright
```

## Daily run

```bash
node apply.mjs                      # all Greenhouse/Lever/Ashby jobs, fit ≥ 8
node apply.mjs --min-fit 9          # best-fit only
node apply.mjs --platforms workday  # Workday assist mode (after you create each account)
node apply.mjs --job 12             # one specific job (id shown on the dashboard)
```

For each job it opens Chrome, uploads the resume, fills name/email/phone/LinkedIn/
company/title/notice-period, then waits. You: answer any custom dropdowns, solve the
CAPTCHA if one appears, click **Submit**, press **Enter** in the terminal → next job.
Realistic pace: **one-page ATSs ~90 seconds/job of your time**; a batch of 15 in ~25 min.

Progress lands in `applied-log.json`; re-runs skip anything already submitted/skipped.

## Zero-code alternative

Install the free **Simplify Copilot** Chrome extension, fill its profile once from
`../profile.json`, then just open each "Open & apply" link on the dashboard — it
autofills, you submit. Slightly less control, zero setup.

## What stays human, always

Account creation + email OTP (Workday), CAPTCHA, the truth attestation, and the final
Submit. Tools that fake these get applications flagged and callback rates near zero —
at VP/CPO level that's a brand you don't want. This setup keeps you fast *and* clean.
