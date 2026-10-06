# Job Agent: LinkedIn + Naukri auto-apply, with a tracking dashboard

An agent that runs on your own computer. It searches LinkedIn and Naukri for jobs that fit your profile, scores each one with Claude, writes a resume tailored to that job, applies from **your own logged-in Chrome**, and logs every job on a dashboard.

```
search ─► read job ─► Claude: match score + tailored resume ─► apply (Easy Apply / Naukri) ─► tracker ─► dashboard
```

## What it does

| | |
|---|---|
| **Finds jobs** | Runs the searches in `config.json` on LinkedIn (Easy Apply, last 7 days) and Naukri (by experience, last 7 days). |
| **Targets Magento / PHP only** | A job is only considered when its own title or description says **Magento, Adobe Commerce or PHP** (`requiredKeywords` in `config.json`). Everything else is skipped before any AI call. Matching jobs are then checked by the AI (location, real job post) and applied to. Searches are Magento, Adobe Commerce and PHP roles. |
| **Tailors the resume** | Reorders and rewrites the summary, skills and bullets for each job. It never invents experience. The PDF is saved as `data/resumes/<job>/Aishwarya_Sharma_Resume.pdf`. |
| **Applies** | LinkedIn: goes through Easy Apply, uploads the tailored PDF and answers the screening questions. Naukri: clicks Apply and answers the recruiter chatbot. |
| **Messages the hiring team** | Writes a short, human-sounding note to the recruiter or hiring manager for every matched job. It names the role, one specific thing from the job post that matches her work, and a real project. With LinkedIn Premium it sends it as an InMail from the "Meet the hiring team" card (after asking you). On the dashboard you can **edit any message and press "Send on LinkedIn"**, or copy it. |
| **Applies on company sites** | When a job says "Apply on company website", the agent opens the site and fills the application: **Workday** (signs in, or creates an account with her email and `ATS_PASSWORD`, then goes through every step), **Greenhouse, Lever, Ashby, SmartRecruiters** and ordinary one-page forms. It uploads the tailored resume and a cover letter, and answers dropdowns and questions with Claude. CAPTCHAs, email verification and sign-ins it can't do are handed to you on the dashboard. |
| **Asks when unsure** | If a question needs data it doesn't have, it asks you on the dashboard instead of guessing. |
| **Tracks** | Dashboard at http://localhost:4321 shows KPIs, applications per day, the pipeline, status edits, notes, links to each tailored resume, and CSV export. |

## Her resume is the source of truth

At the start of every run the agent looks for the newest `~/Downloads/Aishwarya-Sharma-Resume*.pdf` (set `baseResume` in `config.json` to change this). If it's new or changed, Claude re-reads it into `profile.json`: summary, roles and bullets, grouped skills, "at a glance" numbers, project index and credentials. Her screening answers (notice period, CTC…) and contact details are kept. Run `npm run import-resume` to do it by hand.

For every job the steps are: **read the job → create a resume for it → upload that resume → apply**.
- The per-job resume uses the same design as hers (serif name, teal accents, two-column first page, project index, credentials) and stays close to her wording: bullets and skills are reordered and lightly adjusted for the job, never invented.
- LinkedIn Easy Apply and company sites: the new PDF is uploaded in the application and selected.
- Naukri: the new PDF replaces the resume on her Naukri profile just before applying; her own resume from Downloads is put back after the run.

## Which AI it uses (Gemini or Claude)

Set `"provider"` in `config.json`:
- `"gemini"` (default): Google Gemini. Put `GEMINI_API_KEY=…` in `.env`. Both Google key types work: AI Studio keys (`AIza…`, from aistudio.google.com/apikey) and Vertex AI express-mode keys (`AQ.…`, from Google Cloud); the agent picks the right Google endpoint from the key. If a model name isn't available for the key, it tries gemini-2.5-flash / gemini-2.5-pro / gemini-2.0-flash. The model is `"geminiModel"` (default `gemini-flash-latest`; `gemini-pro-latest` is stronger and slower). `"geminiNavigatorModel"` can set a different model for the click-by-click steps.
- `"anthropic"`: Claude. Put `ANTHROPIC_API_KEY=…` in `.env`; the model is `"model"`.

Every AI step uses this setting: matching, tailored resumes, hiring messages, form answers, the Alignerr navigator and resume import. If the key is wrong, the quota or credit runs out, or the model name doesn't exist, the agent stops with a plain message on its dashboard card. Short "busy" (429) replies are retried automatically.

## One-time setup

You need Node.js 20+ and Google Chrome.

```bash
cd job-agent
npm install
cp .env.example .env          # paste your GEMINI_API_KEY (and an ATS_PASSWORD for career sites)
```

1. **Profile.** `profile.json` holds the candidate's data. It is git-ignored, so it never leaves this machine. Either put the supplied `profile.json` in this folder, or generate one from a PDF with `npm run import-resume -- ~/Downloads/resume.pdf`.
2. **Fill the `TODO`s** in `profile.json → applicationAnswers` (notice period, current and expected CTC, relocation, shifts). The agent uses these to answer screening questions.
3. **Start the agent's Chrome:** `npm run chrome`. Chrome doesn't let tools control your everyday profile, so this opens a separate Chrome window with its own profile. **Log in to LinkedIn and Naukri in that window once.** The logins are remembered.

## Daily use

```bash
npm run chrome        # if that Chrome window isn't already open
npm run dashboard     # then open http://localhost:4321
```

Start and stop the agents **from the dashboard**. LinkedIn and Naukri each have their own agent card, so they run independently and can run at the same time. Pick a mode (Practice / Ask before submit / Fully automatic) and a maximum, then press **▶ Start**. When the agent needs you (for example "Submit application to X?"), a yellow box with buttons appears at the top of the dashboard. **■ Stop** ends the run at any time. "Show live log" shows what it's doing.

You can also run it from a terminal; questions are then asked in the terminal. Modes:

| Command | What happens |
|---|---|
| `npm run agent` | **Review mode (default).** It fills everything, then asks `Submit application to X? [Y/n]` before each submit. |
| `npm run agent -- --mode=dry-run` | Finds, scores and tailors resumes only. Jobs show as *Shortlisted*. A later normal run reuses them. |
| `npm run agent -- --mode=auto` | Submits without asking. It still won't guess an answer; those jobs become *Needs attention*. |
| `npm run agent -- --platform=naukri --max=5` | Runs one platform only, with a smaller cap. |

Change searches, the match threshold, `alwaysApplyKeywords`, the per-run cap and excluded titles/companies in `config.json`. `hiringMessage.autoSend` (default `false`) controls whether *Fully automatic* mode sends hiring-team messages without asking.

### Long runs: "Apply to", "Review" and "Keep going until done"
Each agent card has **Apply to** (stop after this many applications), **Review** (stop after looking at this many jobs; 0 = all) and **Keep going until done**. With Keep going on, the agent works through up to 5 result pages per search. When every current job has been reviewed and the target isn't reached, it checks again for new postings every 30 minutes (`recheckMinutes` in `config.json`) instead of stopping. An error on one job never ends the run, a closed tab is reopened, and if the agent process crashes the dashboard restarts it (up to 5 times). Jobs already handled are skipped, so it carries on where it left off. **■ Stop** always ends it.

## Google Forms and Alignerr

- **Google Forms:** when a job's "apply" link, or a link written in the job post, is a Google Form (`forms.gle`, `docs.google.com/forms`), the agent fills it: name, email, phone, ranges like "8+ years", checkboxes, dropdowns, free-text answers written by Claude, and the resume where the form has a file question. It goes through every section and submits. Forms that require a Google sign-in need you to sign in to Google once in the agent's Chrome.
- **Alignerr** (app.alignerr.com) has its own agent card. Alignerr is an app rather than a classic job board, so this agent "looks" at each screen: it numbers the buttons, links and fields, Claude picks the next step (open the Opportunities tab, open a role, Apply, fill the form, upload the resume, Submit), and the agent does it. Every step is shown in the live log. Log in to Alignerr once in the agent's Chrome. The agent lists the open roles, keeps the ones that fit her (software, coding, PHP, JavaScript, full stack…), creates the tailored resume, and applies. Skill assessments and AI interviews are for her to take herself: the agent tells you, and in fully automatic mode marks them "needs attention" and moves on.

## How the agents work through applications

- **Open jobs first, then new ones.** Every round starts with the jobs that aren't finished yet (needs attention, apply on site, shortlisted), best matches first, and only then searches for new postings. Each job gets up to `maxAttemptsPerJob` (3) tries; after that it stays on the dashboard for you.
- **The AI navigator does the hard parts like a person would.** On company career sites (Greenhouse, Lever, Ashby, iCIMS, Taleo, SuccessFactors, Zoho, Keka, Darwinbox, company homepages…) and whenever an Easy Apply / Naukri form gets stuck, it takes over. Every step it looks at a **screenshot** of the page plus a numbered list of all buttons, links and fields, **including forms embedded from another site (iframes)**. Then it does one thing:
  - finds the job and the Apply button, following new tabs;
  - **signs in or creates an account** with her email and `ATS_PASSWORD` from `.env` (the password is never sent to the AI);
  - **uploads the resume** through a file input, an "Upload"/"Attach" button, a small upload menu or a drop zone;
  - fills fields, picks options in dropdowns (also searchable ones), ticks consent boxes, answers screening questions from her data, writes short answers for open questions;
  - **scrolls** to find more fields and the Next/Submit button, reads error messages and fixes them;
  - submits, and only reports "applied" when the site shows a confirmation.
  If an action didn't change anything it tries a different way. Up to `navigatorMaxSteps` (45) steps per application. Every step is shown in the live log.
- **When a person is really needed** (CAPTCHA, an email/SMS verification code, a skill test or video interview, data she never gave), the question appears on the dashboard. In *Fully automatic* mode it waits up to `helpTimeoutMinutes` (3), then moves on and tries again in a later round.
- **⏭ Skip this job** on an agent card drops the job it's working on and goes to the next one.
- Things it never does: solve CAPTCHAs, pay, change account security settings, delete anything, take tests or interviews.

## Statuses on the dashboard

- **Applied**: submitted by the agent, or already applied before.
- **Needs attention**: the agent got stuck on a question or didn't see a confirmation. Open the job and finish it by hand.
- **Apply on site**: the job applies on the company's own site. The tailored resume is ready, so apply manually.
- **Shortlisted**: matched and tailored but not submitted (dry run, or you said no).
- **Interview / Offer / Rejected / Withdrawn**: you set these on the dashboard as replies come in.
- **Skipped**: a poor fit or excluded. Open the row to see why.

## Notes and limits

- **Use it at a human pace.** Automating LinkedIn is against its user agreement, and heavy use can get an account restricted. The defaults are deliberately gentle: review mode, at most 15 applications per run, and a 25 to 70 s pause between applications. Keep them that way.
- **Naukri tailored resumes:** Naukri's Apply always sends the resume on your Naukri profile, so before each Naukri application the agent uploads that job's tailored PDF to the profile, then applies. After the run it puts your normal resume back: set `platforms.naukri.baseResumePath` in `config.json` to your own PDF (e.g. `~/Downloads/Aishwarya-Sharma-Resume.pdf`), otherwise a generated standard version is used. Turn this off with `uploadTailoredResume: false`.
- **Hiring-team messages:** sending needs LinkedIn Premium (InMail) unless you're already connected. Each InMail uses a credit, so review messages in *Ask before submit* mode or send them from the dashboard. Jobs without a "Meet the hiring team" card stay as drafts; copy the message, or use the short version as a connection-request note. Naukri has no candidate-to-recruiter messaging, so Naukri messages are always drafts.
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
src/send-message.mjs   sends one saved message (dashboard "Send on LinkedIn")
src/runner.mjs         starts/stops the agent for the dashboard and relays its questions
dashboard/index.html   the dashboard
```

## When a site gets stuck: `npm run inspect`
Open the page where it got stuck in the agent's Chrome, then run `npm run inspect`. It saves a full screenshot and a text map of the page's buttons, links and fields (email and phone masked) to `data/debug/inspect/`. Send those two files to Claude to get the site fixed.
