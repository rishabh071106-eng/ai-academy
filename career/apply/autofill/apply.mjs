#!/usr/bin/env node
/**
 * Auto-apply assembly line — runs on YOUR laptop (not in a cloud sandbox).
 *
 * Reads career/data/jobs.json + career/apply/profile.json, opens each job in a
 * real Chrome window, auto-fills everything it can, uploads the resume, and:
 *   - Greenhouse / Lever / Ashby: fills the whole one-page form, then pauses so
 *     you can eyeball it and click Submit (CAPTCHA/attestation need a human).
 *   - Workday: jumps to the apply flow; after you sign in / create the tenant
 *     account (email OTP), it clicks "Autofill with Resume" and uploads the PDF.
 *
 * Usage:
 *   npm init -y && npm i playwright        (first time only; uses your Chrome)
 *   node apply.mjs                         # all one-page applies with fit >= 8
 *   node apply.mjs --min-fit 9             # only the best
 *   node apply.mjs --platforms workday     # workday assist mode
 *   node apply.mjs --job 12                # a single job by dashboard id
 *
 * Progress is logged to applied-log.json so re-runs skip finished jobs.
 */
import { chromium } from 'playwright';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import readline from 'readline';

const here = dirname(fileURLToPath(import.meta.url));
const jobs = JSON.parse(readFileSync(join(here, '../../data/jobs.json'), 'utf8'));
const profile = JSON.parse(readFileSync(join(here, '../profile.json'), 'utf8'));
const RESUME = join(here, '../../resume/Rishabh_Sharma_Resume_Product_Leader.pdf');
const LOG = join(here, 'applied-log.json');
const log = existsSync(LOG) ? JSON.parse(readFileSync(LOG, 'utf8')) : {};

const args = process.argv.slice(2);
const opt = (name, dflt) => { const i = args.indexOf('--' + name); return i >= 0 ? args[i + 1] : dflt; };
const MIN_FIT = +opt('min-fit', 8);
const PLATFORMS = opt('platforms', 'greenhouse,lever,ashby').split(',');
const ONLY_JOB = opt('job', null);

const P = profile.my_information;
const FULL_NAME = `${P.legal_first_name} ${P.legal_last_name}`;
const PHONE = `${P.country_phone_code}${P.phone_number}`;

const queue = jobs.filter(j =>
  (ONLY_JOB ? String(j.id) === ONLY_JOB : (PLATFORMS.includes(j.platform) && j.fit_score >= MIN_FIT)) &&
  log[j.id]?.status !== 'submitted' && log[j.id]?.status !== 'skipped'
);
if (!queue.length) { console.log('Nothing in queue. Adjust --min-fit/--platforms, or check applied-log.json'); process.exit(0); }
console.log(`Queue: ${queue.length} job(s)\n` + queue.map(j => `  [${j.id}] ${j.company} — ${j.title} (${j.platform})`).join('\n'));

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const ask = q => new Promise(res => rl.question(q, res));

// Try several strategies to fill a field; never throw if a field doesn't exist.
async function fill(page, labels, value) {
  if (!value) return false;
  for (const l of labels) {
    for (const loc of [
      page.getByLabel(new RegExp(l, 'i')).first(),
      page.locator(`input[name*="${l.toLowerCase().replace(/ /g, '_')}"]`).first(),
      page.getByPlaceholder(new RegExp(l, 'i')).first(),
    ]) {
      try {
        if (await loc.isVisible({ timeout: 400 })) { await loc.fill(String(value)); return true; }
      } catch {}
    }
  }
  return false;
}

async function uploadResume(page) {
  try {
    const input = page.locator('input[type="file"]').first();
    await input.setInputFiles(RESUME, { timeout: 5000 });
    console.log('  ✓ resume uploaded');
    await page.waitForTimeout(3000); // let the ATS parse it
    return true;
  } catch { console.log('  ⚠ no file input found — attach resume manually'); return false; }
}

async function fillCommon(page) {
  await fill(page, ['first name'], P.legal_first_name);
  await fill(page, ['last name'], P.legal_last_name);
  await fill(page, ['full name', '^name$'], FULL_NAME);
  await fill(page, ['email'], P.email);
  await fill(page, ['phone'], PHONE);
  await fill(page, ['linkedin'], profile.links.linkedin);
  await fill(page, ['website', 'portfolio'], profile.links.portfolio);
  await fill(page, ['current company', 'company', 'org'], 'JP Morgan Chase & Co.');
  await fill(page, ['current title', 'title'], 'Vice President — Product Management');
  await fill(page, ['location', 'city'], `${P.city}, ${P.state}, ${P.country}`);
  await fill(page, ['notice'], profile.application_questions_defaults.notice_period.split('.')[0]);
}

async function handleOnePage(page, job) {
  // Lever forms live at /apply; Greenhouse & Ashby show the form on/near the posting.
  if (job.platform === 'lever' && !page.url().endsWith('/apply')) {
    try { await page.getByRole('link', { name: /apply/i }).first().click({ timeout: 4000 }); } catch {}
  }
  if (job.platform === 'greenhouse') {
    try { await page.getByRole('button', { name: /apply/i }).first().click({ timeout: 4000 }); } catch {}
  }
  await page.waitForTimeout(1500);
  await uploadResume(page);   // upload first: GH/Ashby parse it and prefill
  await fillCommon(page);
  console.log('  ✓ auto-fill done — review the form, answer any custom questions, solve CAPTCHA if shown, and click Submit.');
}

async function handleWorkday(page) {
  if (!/\/apply/.test(page.url())) {
    try { await page.getByRole('button', { name: /^apply$/i }).first().click({ timeout: 6000 }); } catch {}
  }
  console.log('  → If asked, sign in / create the account (email OTP goes to your inbox).');
  console.log('  → I will watch for the "Autofill with Resume" option for 3 minutes...');
  try {
    const auto = page.getByText(/autofill with resume/i).first();
    await auto.click({ timeout: 180000 });
    await uploadResume(page);
    console.log('  ✓ resume handed to Workday parser — audit every screen (dates/titles), then continue the wizard.');
  } catch { console.log('  ⚠ Autofill option not seen — continue manually; answers are in profile.json / the playbook.'); }
}

const browser = await chromium.launch({ headless: false, channel: 'chrome' }).catch(() => chromium.launch({ headless: false }));
const ctx = await browser.newContext();

for (const job of queue) {
  console.log(`\n━━ [${job.id}] ${job.company} — ${job.title}\n   ${job.apply_url}`);
  const page = await ctx.newPage();
  try {
    await page.goto(job.apply_url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    if (job.platform === 'workday') await handleWorkday(page);
    else await handleOnePage(page, job);
  } catch (e) { console.log('  ⚠ ' + e.message.split('\n')[0]); }
  const a = (await ask('  [Enter]=submitted  s=skip  o=still open, next job  q=quit > ')).trim().toLowerCase();
  if (a === 'q') break;
  log[job.id] = { company: job.company, title: job.title, status: a === 's' ? 'skipped' : a === 'o' ? 'open' : 'submitted', at: new Date().toISOString() };
  writeFileSync(LOG, JSON.stringify(log, null, 2));
  if (a !== 'o') await page.close();
}
rl.close();
console.log(`\nDone. Log: ${LOG} — mirror statuses onto the dashboard for the full picture.`);
await browser.close();
