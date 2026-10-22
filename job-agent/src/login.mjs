// Signing in to a job site with her Google account. Gmail is logged in in the agent's Chrome,
// so "Continue with Google" needs no password: pick her account in Google's pop-up, allow, done.
// Used when LinkedIn / Naukri / Alignerr show a login page, and by the navigator on company sites.
import { GOOGLE_RULES, navigate } from "./navigator.mjs";
import { findBaseResume } from "./profile-sync.mjs";
import { loadConfig, loadProfile, log, sleep } from "./util.mjs";

const PASSWORD_TOKEN = "{{PASSWORD}}";

/**
 * Makes sure `site` is usable: already logged in → fine; else sign in with Google; else create
 * an account with her email and ATS_PASSWORD (the navigator types the {{PASSWORD}} token and
 * reads any verification code / link from her Gmail); if the email is already registered,
 * "Forgot password" → reset link from Gmail → new password → sign in. Returns true when logged in.
 */
export async function ensureAccount(page, site, { isLoggedIn, home } = {}) {
  const loggedIn = async () => (isLoggedIn ? isLoggedIn(page) : !(await looksLoggedOut(page)));
  if (await loggedIn()) return true;
  if (await signInWithGoogle(page, site, { isLoggedIn: () => loggedIn(), returnTo: home })) return true;
  if (!process.env.ATS_PASSWORD) {
    log("warn", `  ${site}: no Google sign-in and no ATS_PASSWORD in .env to create an account — add one`);
    return false;
  }
  const profile = loadProfile();
  log("info", `  ${site}: creating an account for ${profile.email} (or recovering the existing one)…`);
  const r = await navigate(page, {
    goal: `Get ${site} logged in as ${profile.email}. Steps: open Register / Sign up / Create account; fill her details (name ${profile.name}, email ${profile.email}, phone ${profile.phone}, city ${profile.city}, experience ${profile.totalExperienceYears} years, current role ${profile.headline}); for every password field type exactly ${PASSWORD_TOKEN}; accept the terms; submit. If the site emails a verification code or link, use check_email("${site}") and finish the verification. If it says the email is already registered / account exists, go to Login → "Forgot password", enter ${profile.email}, use check_email("${site}") to get the reset link or code, set the new password to ${PASSWORD_TOKEN}, then log in with ${profile.email} and ${PASSWORD_TOKEN}. Upload her resume (upload_resume) if the sign-up asks for one; skip optional profile steps. When ${site} shows her as logged in, use done with status "applied" (meaning: logged in). Only use need_user for a CAPTCHA or an SMS code.`,
    rules: GOOGLE_RULES(profile.email),
    profile,
    resumePath: findBaseResume(loadConfig().baseResume)?.path ?? null,
    mode: "auto",
    maxSteps: 40,
  }).catch((e) => ({ status: "needs_attention", note: e.message }));
  if (home) await page.goto(home, { waitUntil: "domcontentloaded" }).catch(() => {});
  await sleep(2500);
  const ok = await loggedIn();
  log(ok ? "ok" : "warn", ok ? `  ${site}: logged in` : `  ${site}: couldn't get logged in (${r.note}) — log in once in the agent's Chrome window`);
  return ok;
}

/** Heuristic for sites we have no selectors for: visible Log in / Sign up links in the header mean logged out. */
export async function looksLoggedOut(page) {
  if (/\/(login|signin|sign-in|signup|sign-up|register|auth)\b/i.test(page.url()) || /accounts\.google\.com/.test(page.url())) return true;
  const n = await page
    .locator("header, nav, [class*=header], [class*=navbar], [class*=topbar]")
    .getByRole("link", { name: /^(log ?in|sign ?in|sign ?up|register|join( now)?|create account)$/i })
    .or(page.locator("header, nav, [class*=header], [class*=navbar]").getByRole("button", { name: /^(log ?in|sign ?in|sign ?up|register|join( now)?)$/i }))
    .filter({ visible: true })
    .count()
    .catch(() => 0);
  return n > 0;
}

/**
 * Tries to sign `page` in with Google. Returns true when the site looks logged in afterwards.
 * `isLoggedIn(page)` is the site's own check; `returnTo` is reloaded at the end.
 */
export async function signInWithGoogle(page, site, { isLoggedIn, returnTo } = {}) {
  const profile = loadProfile();
  log("info", `  ${site} is logged out — signing in with Google as ${profile.email}…`);
  const r = await navigate(page, {
    goal: `Sign in to ${site} with her Google account (${profile.email}). Find "Sign in" / "Log in", choose "Sign in with Google" / "Continue with Google", pick ${profile.email} in Google's pop-up, allow, and wait until ${site} shows her as logged in. Then use done with status "applied" (meaning: signed in). If ${site} only offers email + password and no Google button, use need_user.`,
    rules: GOOGLE_RULES(profile.email),
    profile,
    mode: "auto",
    maxSteps: 15,
  }).catch((e) => ({ status: "needs_attention", note: e.message }));
  if (returnTo) await page.goto(returnTo, { waitUntil: "domcontentloaded" }).catch(() => {});
  await sleep(2500);
  const ok = isLoggedIn ? await isLoggedIn(page) : r.status === "applied";
  log(ok ? "ok" : "warn", ok ? `  signed in to ${site} with Google` : `  couldn't sign in to ${site} with Google (${r.note}); log in once in the agent's Chrome window`);
  return ok;
}
