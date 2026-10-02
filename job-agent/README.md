# Job Agent: LinkedIn + Naukri auto-apply, with a tracking dashboard

An agent that runs on your own computer. It searches LinkedIn and Naukri for jobs that fit your profile, scores each one with Claude, writes a resume tailored to that job, applies from **your own logged-in Chrome**, and logs every job on a dashboard.

```
search ─► read job ─► Claude: match score + tailored resume ─► apply (Easy Apply / Naukri) ─► tracker ─► dashboard
```

## What it does

| | |
|---|---|
| **Finds jobs** | Runs the searches in `config.json` on LinkedIn (Easy Apply, last 7 days) and Naukri (by experience, last 7 days). |
| **Scores them** | Claude rates each job against `profile.json`, treating her as full-stack (Magento/PHP back end and React/Next.js front end). Any job that mentions a word in `alwaysApplyKeywords` (Magento, Adobe Commerce, React, Next.js) is applied to whatever the score. Others need `minMatchScore` (55). |
| **Tailors the resume** | Reorders and rewrites the summary, skills and bullets for each job. It never invents experience. The PDF is saved as `data/resumes/<job>/Aishwarya_Sharma_Resume.pdf`. |
| **Applies** | LinkedIn: goes through Easy Apply, uploads the tailored PDF and answers the screening questions. Naukri: clicks Apply and answers the recruiter chatbot. |
| **Messages the hiring team** | Writes a personal note to the recruiter or hiring manager for every matched job. On LinkedIn it sends it with the **Message** button on the "Meet the hiring team" card when LinkedIn allows that (after asking you). Otherwise the message is saved on the dashboard with a **Copy** button. |
| **Asks when unsure** | If a question needs data it doesn't have (notice period, CTC…) it **pauses and asks you** instead of guessing. |
| **Tracks** | Dashboard at http://localhost:4321 shows KPIs, applications per day, the pipeline, status edits, notes, links to each tailored resume, and CSV export. |

## One-time setup

You need Node.js 20+ and Google Chrome.

```bash
cd job-agent
npm install
cp .env.example .env          # paste your ANTHROPIC_API_KEY
```

1. **Profile.** `profile.json` holds the candidate's data. It is git-ignored, so it never leaves this machine. Either put the supplied `profile.json` in this folder, or generate one from a PDF with `npm run import-resume -- ~/Downloads/resume.pdf`.
2. **Fill the `TODO`s** in `profile.json → applicationAnswers` (notice period, current and expected CTC, relocation, shifts). The agent uses these to answer screening questions.
3. **Start the agent's Chrome:** `npm run chrome`. Chrome doesn't let tools control your everyday profile, so this opens a separate Chrome window with its own profile. **Log in to LinkedIn and Naukri in that window once.** The logins are remembered.

## Daily use

```bash
npm run chrome        # if that Chrome window isn't already open
npm run dashboard     # then open http://localhost:4321
```

Start and stop the agent **from the dashboard**: pick a mode (Practice / Ask before submit / Fully automatic), the platforms and a maximum, then press **▶ Start**. When the agent needs you (for example "Submit application to X?"), a yellow box with buttons appears at the top of the dashboard. **■ Stop** ends the run at any time. "Show live log" shows what it's doing.

You can also run it from a terminal; questions are then asked in the terminal. Modes:

| Command | What happens |
|---|---|
| `npm run agent` | **Review mode (default).** It fills everything, then asks `Submit application to X? [Y/n]` before each submit. |
| `npm run agent -- --mode=dry-run` | Finds, scores and tailors resumes only. Jobs show as *Shortlisted*. A later normal run reuses them. |
| `npm run agent -- --mode=auto` | Submits without asking. It still won't guess an answer; those jobs become *Needs attention*. |
| `npm run agent -- --platform=naukri --max=5` | Runs one platform only, with a smaller cap. |

Change searches, the match threshold, `alwaysApplyKeywords`, the per-run cap and excluded titles/companies in `config.json`. `hiringMessage.autoSend` (default `false`) controls whether *Fully automatic* mode sends hiring-team messages without asking.

## Statuses on the dashboard

- **Applied**: submitted by the agent, or already applied before.
- **Needs attention**: the agent got stuck on a question or didn't see a confirmation. Open the job and finish it by hand.
- **Apply on site**: the job applies on the company's own site. The tailored resume is ready, so apply manually.
- **Shortlisted**: matched and tailored but not submitted (dry run, or you said no).
- **Interview / Offer / Rejected / Withdrawn**: you set these on the dashboard as replies come in.
- **Skipped**: a poor fit or excluded. Open the row to see why.

## Notes and limits

- **Use it at a human pace.** Automating LinkedIn is against its user agreement, and heavy use can get an account restricted. The defaults are deliberately gentle: review mode, at most 15 applications per run, and a 25 to 70 s pause between applications. Keep them that way.
- **Naukri uses the resume on your Naukri profile.** Naukri's one-click apply attaches that resume, not a per-job file. The tailored PDF is still saved for each Naukri job, for reference or to upload manually.
- **Hiring-team messages:** LinkedIn only lets you message people you're connected to, people with open profiles, or anyone if you have Premium (InMail). When it won't, the message is kept as a draft on the dashboard; copy it, or use the short version as a connection-request note. Naukri has no candidate-to-recruiter messaging, so Naukri messages are always drafts.
- Site layouts change. If a selector stops matching, the job becomes *Needs attention* instead of a wrong submission. Selectors live in `src/linkedin.mjs` and `src/naukri.mjs`.
- All data stays local: `data/applications.json`, `data/resumes/` and `profile.json` are git-ignored.
- To preview the dashboard with sample rows, run `npm run demo-data`. Delete `data/applications.json` before real use.

## Files

```
src/agent.mjs          orchestration (search → score → tailor → apply → track)
src/linkedin.mjs       LinkedIn search + Easy Apply
src/naukri.mjs         Naukri search + apply + chatbot questionnaire
src/forms.mjs          generic form reader/filler for application dialogs
src/llm.mjs            Claude calls: match + tailor, answer questions, import resume
src/resume.mjs         tailored resume → HTML → PDF
src/tracker.mjs        data/applications.json store
src/server.mjs         dashboard server + API
src/runner.mjs         starts/stops the agent for the dashboard and relays its questions
dashboard/index.html   the dashboard
```
