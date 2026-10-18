// Signing in to a job site with her Google account. Gmail is logged in in the agent's Chrome,
// so "Continue with Google" needs no password: pick her account in Google's pop-up, allow, done.
// Used when LinkedIn / Naukri / Alignerr show a login page, and by the navigator on company sites.
import { GOOGLE_RULES, navigate } from "./navigator.mjs";
import { loadProfile, log, sleep } from "./util.mjs";

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
