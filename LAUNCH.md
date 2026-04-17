# 🚀 Launch Today — 5 Steps, ~10 minutes

Do these in order. Each step is idiot-proof on purpose.

---

## Step 1 — Get an Anthropic API key (2 min)

1. Go to https://console.anthropic.com → sign up with Google/email.
2. Settings → API Keys → **Create Key** → copy the `sk-ant-...` value.
3. Add **$5 of credit** (Settings → Plans & Billing). That lasts months.

**Keep the key safe. Don't paste it in chat, Git, or anywhere public.**

---

## Step 2 — Get a Formspree form (1 min)

The subscribe form needs somewhere to send emails. Formspree is free for 50 submissions/month.

1. Go to https://formspree.io → sign up (free).
2. Click **+ New Form** → name it "AI Academy Subscribe" → create.
3. Copy the form ID (the URL looks like `https://formspree.io/f/xyzabcd` — you want `xyzabcd`).
4. Open `index.html` and replace **`YOUR_FORMSPREE_ID`** with that ID (one replacement, near the bottom of the file).

---

## Step 3 — Push to GitHub (3 min)

Open Terminal on your Mac:

```bash
cd /Users/admin/Desktop/EVENT/ai-academy

# Install generator dependencies (one-time)
npm install

# Init git
git init
git add .
git commit -m "initial: ai-academy"

# Create GitHub repo + push (requires the gh CLI: brew install gh, then gh auth login)
gh repo create ai-academy --public --source=. --push
```

If you don't have `gh` installed: go to github.com, create a new public repo called `ai-academy`, then follow GitHub's "push an existing repo" instructions (2 commands).

---

## Step 4 — Add your API key as a GitHub secret (1 min)

1. GitHub → your `ai-academy` repo → **Settings** tab.
2. Sidebar: **Secrets and variables** → **Actions** → **New repository secret**.
3. Name: `ANTHROPIC_API_KEY`
4. Value: paste your `sk-ant-...` key.
5. Save.

Now the daily workflow can use it.

---

## Step 5 — Deploy to Vercel (3 min)

1. Go to https://vercel.com → sign up **with your GitHub account** (it auto-connects).
2. Click **Add New → Project** → pick `ai-academy` → **Import**.
3. Settings:
   - Framework Preset: **Other**
   - Root directory: `./` (default)
   - Build command: leave blank
   - Output directory: leave blank
4. Click **Deploy**.

After ~30 seconds, you'll have a live URL like `ai-academy-xyz.vercel.app`.

**That's it. Your site is live.**

---

## Verify it works

- Open the Vercel URL → homepage with 5 chapters should load.
- Click a chapter → should render with share bar.
- Click a share button → should open X/LinkedIn/WhatsApp share dialog.
- Subscribe an email → check your Formspree inbox.

---

## Trigger the daily generator NOW (optional, to test)

You don't have to wait until tomorrow 10 AM IST for the first auto-chapter.

1. GitHub → your repo → **Actions** tab.
2. Click **"Daily chapter generator"** (left sidebar).
3. Click **Run workflow** button (top right) → **Run workflow**.
4. Watch the run. When it succeeds, Vercel auto-redeploys and your 6th chapter is live.

If it fails: click the run to see the error. 90% of the time it's a missing API key or unfunded account.

---

## After launch

**Add your custom domain (if you bought one):**
- Vercel → Project → Settings → Domains → Add.
- Follow the DNS instructions Vercel shows.

**Change the daily time:**
- Edit `.github/workflows/daily.yml` cron (currently 04:30 UTC = 10:00 AM IST).

**Add more topics so the queue doesn't run out:**
- Edit `scripts/sources.json` → `topicsQueue` array. Add as many as you want.

**Swap to a cheaper/faster model:**
- `scripts/generate.mjs` line ~90 → change `claude-opus-4-6` to `claude-haiku-4-5-20251001` for ~10× lower cost.

**Set SITE_URL for correct RSS/sitemap:**
- GitHub → repo Settings → Secrets and variables → Actions → Variables tab → New variable `SITE_URL` = `https://yourdomain.com`.
- Then edit `.github/workflows/daily.yml`: under `env`, add:
  ```yaml
  SITE_URL: ${{ vars.SITE_URL }}
  ```

---

## Cost after launch

- Vercel: **$0** (hobby plan, 100 GB bandwidth/mo free)
- GitHub Actions: **$0** (free for public repos)
- Formspree: **$0** (50 submissions/mo free)
- Anthropic: **~$0.30–$3/month** depending on model
- Domain: **~$10/year** (optional)

**Total: under $5/month, even with a custom domain.**

---

If anything breaks during launch, check:
1. Generator logs in GitHub Actions
2. Vercel deployment logs
3. Browser console on your live site

And come back here — I can help debug any specific error message you paste.
