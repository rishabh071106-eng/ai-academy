# AI Academy

A static site that teaches AI, one chapter at a time. A new chapter is auto-generated every day by a GitHub Actions cron job that calls the Claude API, using a queue of topics and a set of RSS feeds as "what's happening now" signal.

---

## What's in this folder

```
ai-academy/
├─ index.html                  ← homepage (chapter grid)
├─ chapters/                   ← one HTML file per chapter (shareable URLs)
│  ├─ what-is-ai-really.html
│  ├─ how-llms-work-without-math.html
│  ├─ prompt-engineering-that-works.html
│  ├─ rag-vs-fine-tune-vs-prompt.html
│  └─ agents-when-ai-uses-tools.html
├─ assets/
│  ├─ style.css                ← all styling (dark theme)
│  └─ chapters.json            ← index of published chapters
├─ scripts/
│  ├─ generate.mjs             ← the daily generator (Node + Claude SDK)
│  └─ sources.json             ← RSS feeds + topic queue
├─ .github/workflows/daily.yml ← daily cron (GitHub Actions)
└─ package.json
```

---

## Run it locally (right now)

```bash
cd ai-academy
python3 -m http.server 8080
```

Then open http://localhost:8080

Every chapter has its own URL like
`http://localhost:8080/chapters/what-is-ai-really.html` — that's what you share.

---

## Generate a new chapter manually

1. Get an Anthropic API key from https://console.anthropic.com
2. `npm install` (one time)
3. Run:

```bash
ANTHROPIC_API_KEY=sk-ant-... npm run generate
```

This will:
- Pick the next topic from `scripts/sources.json` (`topicsQueue`)
- Fetch headlines from configured RSS feeds for context
- Call Claude to write the chapter
- Write a new HTML file in `chapters/`
- Update `assets/chapters.json` so the homepage shows it
- Update the previous chapter's "Next" link

Re-run any time. Cost per chapter: roughly $0.10 with Opus, $0.01 with Haiku (edit `model` in `generate.mjs`).

---

## Go live and automate (one-time setup, ~10 minutes)

### 1. Push to GitHub (free)

```bash
cd ai-academy
git init
git add .
git commit -m "initial: ai-academy site"
gh repo create ai-academy --public --source=. --push
```

(Or use the GitHub web UI — new repo, upload files.)

### 2. Add your Anthropic key as a secret

GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**
- Name: `ANTHROPIC_API_KEY`
- Value: your `sk-ant-...` key

### 3. Deploy to Vercel (free, recommended)

- Sign up at https://vercel.com
- "Add New → Project" → import your GitHub repo
- Framework preset: **Other** (it's a static site)
- Root directory: leave as `/`
- Deploy

You now have a live URL like `ai-academy-xyz.vercel.app`. Every time the GitHub Action commits a new chapter, Vercel redeploys in ~20 seconds.

### 4. (Optional) Point your domain

In Vercel → Project → Settings → Domains, add your custom domain. Vercel tells you which DNS records to set at your registrar.

---

## Customize it

**Change the topic queue** — edit `scripts/sources.json`. The queue is consumed top-to-bottom. Add as many topics as you want.

**Change the house voice** — edit the `systemPrompt` in `scripts/generate.mjs`. That's where the style rules live.

**Change the schedule** — edit the cron in `.github/workflows/daily.yml`. Default: every day at 04:30 UTC. Standard 5-field cron.

**Change the model** — inside `generate.mjs`:
- `claude-opus-4-6` — best quality, ~$0.10/chapter
- `claude-sonnet-4-6` — great middle ground, ~$0.03/chapter
- `claude-haiku-4-5-20251001` — fastest & cheapest, ~$0.01/chapter

**Add email subscriptions** — the homepage has a signup form that currently just shows a success message. Hook it to:
- Mailchimp / ConvertKit (paste their embed code)
- Buttondown (simple, developer-friendly)
- A Google Sheet via a Google Apps Script webhook

**Add analytics** — paste a Plausible/GA snippet before `</head>` in `index.html` and each chapter template.

---

## Cost estimate (monthly)

| Item | Cost |
|---|---|
| Domain (optional) | ~$1/mo |
| Vercel hosting | **$0** (hobby plan is enough) |
| GitHub Actions | **$0** (free for public repos) |
| Claude API (~30 chapters/mo with Haiku) | ~$0.30 |
| Claude API (~30 chapters/mo with Opus)  | ~$3 |

**Under $5/mo, easy.**

---

## Things this does NOT do (yet)

- **No user accounts / comments.** Static site. Add Disqus if you want comments.
- **No search.** Add Pagefind (free) for client-side search in 5 minutes when you have enough chapters.
- **No newsletter backend.** Form is a placeholder. Connect it to a real service.
- **No dark/light toggle.** Site is dark-mode-only by design (horror-of-AI vibes). Change `:root` in `style.css` for light.
- **No RSS output.** Easy to add — iterate over `chapters.json` and write an `rss.xml` in the generator.

---

## Troubleshooting

**"Generator writes garbage"** — your API key probably isn't set, or Claude returned non-JSON. Check the error in Actions logs. Try running locally first.

**"Previous chapter's Next link didn't update"** — the regex fallback didn't match. Manually edit the previous chapter's nav-next block, or strengthen the regex in `generate.mjs`.

**"Chapter topic feels stale"** — refill `topicsQueue` in `scripts/sources.json`. The generator shifts one off each run.

**"I don't want daily. I want weekly."** — change cron to `30 4 * * 1` (Monday 04:30 UTC only).

---

Built with the boring parts done for you. Go write.
