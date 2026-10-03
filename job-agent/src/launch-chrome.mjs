// npm run chrome — starts the agent's Chrome with the DevTools port open.
// Chrome (v136+) refuses remote debugging on your *default* profile, so this uses a
// dedicated profile in job-agent/.chrome-profile. Log in to LinkedIn, Naukri and Alignerr in
// that window once; the logins persist for every later run. (The agents also start this
// Chrome by themselves when it isn't running.)
import { launchChrome } from "./chrome.mjs";
import { log } from "./util.mjs";

try {
  const url = await launchChrome();
  if (url) {
    log("ok", `Chrome is running with DevTools at ${url} (profile: .chrome-profile).`);
    log("info", "Log in to LinkedIn, Naukri and Alignerr in that window (first time only), then start the agents from the dashboard.");
  } else log("err", "Chrome started but didn't open its DevTools port. Quit Chrome completely (Cmd+Q) and run npm run chrome again.");
} catch (e) {
  log("err", e.message);
  process.exit(1);
}
process.exit(0);
