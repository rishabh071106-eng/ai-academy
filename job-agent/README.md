# Autonomous Job Application Agent

A self-running agent that finds **Director / VP / Head of Product** roles,
tailors your resume + cover letter per job (choosing AI-leadership vs
product-leadership emphasis from your master resume), fills the application
form, and submits — without intervention where it safely can.

**Hard exclusions:** JPMorgan Chase and Wells Fargo (and any agency hiring on
their behalf) are blocked at three layers: fuzzy company-name matching, an
instruction in the scoring prompt, and a mechanical re-check before any
application is built.

## How it works

```
discover ──> prefilter ──> score ──> tailor ──> apply ──> record
 (ATS APIs    (title regex,  (Claude:   (Claude:    (Playwright:  (SQLite —
  + Claude     blocklist)     fit 0-100, resume JSON  scrape form,  never apply
  web search)                 seniority, -> DOCX +    Claude maps   twice)
                              blocklist) cover letter) answers, submit)
```

1. **Discover** — pulls jobs from public Greenhouse/Lever/Ashby board APIs for
   companies you watch, plus Claude server-side web search for broad discovery.
2. **Score** — Claude rates fit 0–100, verifies seniority (Director+ only),
   re-checks the blocklist semantically (catches staffing-agency postings), and
   picks which resume emphasis to use.
3. **Tailor** — rewrites your master resume for the job (never inventing facts),
   renders a DOCX, writes a cover letter.
4. **Apply** — opens the posting headless, scrapes every form field, has Claude
   map each field to a truthful answer from `profile/profile.yaml`, uploads the
   resume, and submits. Saves a confirmation screenshot.
5. **Record** — SQLite state guarantees no duplicate applications.

### When it will NOT auto-submit (by design)

- **CAPTCHA or login wall** (LinkedIn Easy Apply, most Workday instances) —
  these actively block automation. The agent saves a complete **review packet**
  instead: tailored resume, cover letter, planned answers, and a screenshot in
  `applications/<company>--<role>/`. You finish those in two minutes each.
- **A required question it can't answer truthfully** from your profile (e.g.
  exact salary expectation, references). It will never guess — review packet.

Everything else (Greenhouse, Lever, Ashby standard forms — a large share of
senior product roles) is submitted automatically.

## Setup

```bash
cd job-agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
export ANTHROPIC_API_KEY=sk-ant-...
```

Then personalize:

1. `profile/profile.yaml` — confirm notice period, compensation stance, and
   screening answers. **The agent only ever answers from this file.**
2. `config.yaml` — add companies you care about under `companies:` (their
   Greenhouse/Lever/Ashby slugs), tune `web_queries`, adjust caps.

## Run

```bash
python -m src.main --dry-run        # discover + score + tailor only (recommended first run)
python -m src.main                  # one full run, auto-submitting
python -m src.main --loop --interval-hours 6   # self-running daemon
```

For a server/VPS, cron works too:

```cron
0 8,14,20 * * * cd /path/to/job-agent && .venv/bin/python -m src.main >> agent.log 2>&1
```

A GitHub Actions workflow is included at `.github/workflows/job-agent.yml`
(runs on a schedule; needs the `ANTHROPIC_API_KEY` repo secret; note GitHub
only triggers scheduled workflows from the **default branch**).

## Safety dials (config.yaml -> policy)

| Key | Default | Meaning |
|---|---|---|
| `min_fit_score` | 70 | Don't apply below this fit score |
| `max_applications_per_run` | 5 | Hard cap per run — protects your reputation |
| `auto_submit` | true | `false` = fill + screenshot, you click submit |
| `dry_run` | false | Never opens a browser at all |

**Recommended first week:** run with `--dry-run`, read the scoring decisions in
the console output and the tailored packages in `applications/`, then flip to
live. Your name goes on every submission — make sure you like what it writes
before letting it loose.

## Costs & notes

- Model is `claude-fable-5` (set in `config.yaml`); switch to `claude-opus-4-8`
  to halve cost. Fable 5 requires your Anthropic org to have 30-day data
  retention (the default) — not available under zero-data-retention.
- A run that scores ~20 jobs and applies to 5 typically costs a few dollars.
- `state/` and `applications/` contain personal data and are git-ignored.
- Some ATS terms of service restrict automation; the agent identifies itself
  honestly (your real details, no captcha evasion) and only automates form
  entry you'd otherwise type by hand. Use your judgment.
