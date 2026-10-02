// node src/send-message.mjs <applicationId>
// Sends the saved (possibly edited) hiring-team message for one job. Used by the dashboard's "Send on LinkedIn".
import { connect } from "./browser.mjs";
import { sendForJob } from "./linkedin.mjs";
import * as tracker from "./tracker.mjs";

const id = process.argv[2];
const row = tracker.loadAll().find((r) => r.id === id);
const done = (result, code = 0) => {
  console.log(JSON.stringify(result));
  process.exit(code);
};
if (!row) done({ status: "error", note: "Job not found" }, 1);
if (row.platform !== "linkedin") done({ status: "draft", note: "Only LinkedIn supports messaging the hiring team" }, 1);
if (!row.hiringMessage?.full) done({ status: "draft", note: "No message saved for this job" }, 1);

let page;
try {
  const { context } = await connect();
  page = await context.newPage();
  const r = await sendForJob(page, row);
  tracker.update(id, { messageStatus: r.status, messageNote: r.note, ...(r.status === "sent" ? { messageSentAt: new Date().toISOString() } : {}) });
  await page.close().catch(() => {});
  done(r);
} catch (e) {
  await page?.close().catch(() => {});
  done({ status: "draft", note: e.message.split("\n")[0] }, 1);
}
