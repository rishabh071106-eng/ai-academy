# Direct-Apply Playbook — Rishabh Sharma (Product Leader)

Researched 2 Aug 2026. Companion to `profile.json` (the prefill data pack) and the job dashboard.

## The honest picture

| ATS | Account? | Effort per apply | What can be pre-done for you |
|---|---|---|---|
| **Greenhouse** | No | ~2–3 min | Everything except CAPTCHA + Submit click |
| **Lever** | No | ~2 min | Everything except Submit (only name+email required by default) |
| **Ashby** | No | ~2–3 min | Everything except Submit |
| **Workday** | Yes — one account **per company tenant** | ~10–15 min first time, ~5 min after | Job harvesting, all field answers, resume; **you** do account+email OTP, review, Submit |

Human-only steps everywhere: account credentials, email verification codes (OTP), CAPTCHA, the truth-attestation checkbox, and the final Submit. Fire-and-forget bulk tools (LazyApply etc.) skip these — that's why they get accounts flagged and ~0.5% callback rates. At VP/CPO level, recruiters see timestamps and identical-blast patterns; assisted-but-human is both safer and better for your brand.

## Workday fast path (per company)

1. Open the job URL from the dashboard → **Apply** (appending `/apply` to the posting URL usually jumps straight there).
2. First time at this company: **Create Account** — use rishabh071106@gmail.com + one strong password you reuse mentally across tenants; enter the 6-digit email code.
3. Pick **Autofill with Resume** → upload `career/resume/Rishabh_Sharma_Resume_Product_Leader.pdf` (built single-column with standard headings specifically so Workday parses it cleanly).
4. Audit every screen — Workday misparses ~1/3 of autofilled fields (dates, titles). Correct against `profile.json`.
5. **Application Questions**: answer from the question bank below.
6. Voluntary Disclosures: optional; "I don't wish to answer" is always safe.
7. Review → Submit. You cannot edit after submitting — only withdraw.
8. Same company later: **Use My Last Application** (verify it didn't drop your first role — known bug).

## Standard question bank (copy-paste answers)

- **Authorized to work in India**: Yes. **Sponsorship**: No.
- **Notice period**: "Serving notice — last working day 11 Sep 2026; can join from 12 Sep 2026." (~6 weeks — counts as near-immediate for senior reqs.)
- **Earliest start date**: 2026-09-12 (or "mid-September 2026").
- **Current CTC**: ₹48L fixed — only if mandatory (numeric only in Workday: 4800000).
- **Expected CTC**: ask ₹95L (numeric: 9500000), negotiate toward ₹1 Cr total. Competing offer (₹75L fixed + ~10% bonus ≈ ₹82.5L) is the private walk-away floor — never name the company on a form; mention "competing offer in hand, deciding in coming weeks" at recruiter screens to compress timelines.

### Comp targeting at ₹95L–1Cr
- **In band**: CPO/Head-of-Product exec-search mandates, big-tech Director/GPM (Google GPM ₹1Cr+, Intuit VP well above, Salesforce/Adobe/Uber Director ₹1Cr±), Visa/Mastercard Director (₹90L–1.3Cr with equity/bonus), NatWest/Wells Fargo Director-ED grades (upper band), the ₹79–96L Senior Director Consumer Lending (top of band = the ask).
- **Below band — deprioritize**: Lead/Senior-PM/AVP-grade reqs (fit ≤6), most Indian-fintech Associate-Director seats unless heavy ESOPs are on the table. Startup CPO roles: judge cash+ESOP mix, ask for ₹95L cash-heavy.
- At ₹95L+, negotiation happens at offer stage, not screening — keep forms at 9500000 and let scope/level do the talking.

### Timeline math (today = 2 Aug)
- Aug 2–14: applications + recruiter screens (senior processes take 4–8 weeks — start everything now).
- Aug 15 – Sep 5: interview loops; use the competing offer's decision deadline to compress.
- Sep 11: JPM last working day. Any new offer landing after this is still fine — you join later; but an offer before ~Sep 1 lets you decide between it and the one in hand without a gap.
- **How did you hear about us**: Company website.
- **Previously worked for this company**: No (note: answer Yes at Citi/Standard Bank contexts only if the form counts vendor/consultant engagements — read the fine print).
- **Relatives at company**: No.
- **Willing to relocate**: Based in Bengaluru; open to discussion.

## Per-tenant registration tracker

Keep this updated as accounts get created (same email everywhere — it keys your candidate record):

| Company (tenant) | Account created | Applied to | Date |
|---|---|---|---|
| _add as you go_ | | | |

## Pacing rules (avoid bot-detection and recruiter-side red flags)

- Max ~2–3 applications per company per week; never burst 10 in an hour at one tenant.
- Duplicate applications to the same requisition are blocked per account anyway.
- Keep resume identical across a company's reqs, tailored *cover letters/blurbs* per req (dashboard provides these).
- Real browser, normal pacing. No headless mass-submission.

## Optional accelerator

Install **Simplify Copilot** (free Chrome extension — fills forms from your profile, never auto-submits; ~85–90% accuracy on Greenhouse/Lever/Ashby, ~70% on Workday). Load it with the data in `profile.json` once and every form becomes review-and-click.
