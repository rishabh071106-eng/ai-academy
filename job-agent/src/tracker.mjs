import fs from "node:fs";
import path from "node:path";
import { DATA_DIR, readJson } from "./util.mjs";

export const TRACKER_FILE = path.join(DATA_DIR, "applications.json");

export const STATUSES = [
  "shortlisted",     // matched, resume tailored, not yet applied (dry run / you chose to skip)
  "applied",
  "needs_attention", // agent got stuck on a question, apply it by hand
  "external",        // job applies on the company's own site
  "interview",
  "offer",
  "rejected",
  "skipped",         // low match or excluded
  "withdrawn",
];

export function loadAll() {
  return readJson(TRACKER_FILE, []);
}

function saveAll(rows) {
  const tmp = `${TRACKER_FILE}.${process.pid}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(rows, null, 2));
  fs.renameSync(tmp, TRACKER_FILE);
}

// LinkedIn and Naukri agents (and the dashboard) can write at the same time; a lock file makes
// each read-modify-write atomic across processes.
const LOCK = TRACKER_FILE + ".lock";
const pause = (ms) => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
function withLock(fn) {
  for (let i = 0; ; i++) {
    try {
      fs.closeSync(fs.openSync(LOCK, "wx"));
      break;
    } catch (e) {
      if (e.code !== "EEXIST") throw e;
      try {
        if (Date.now() - fs.statSync(LOCK).mtimeMs > 10000) fs.rmSync(LOCK, { force: true }); // stale
      } catch {}
      if (i > 400) throw new Error("Tracker is locked");
      pause(25);
    }
  }
  try {
    return fn();
  } finally {
    fs.rmSync(LOCK, { force: true });
  }
}

export const keyOf = (platform, jobId) => `${platform}:${jobId}`;

export function find(platform, jobId) {
  return loadAll().find((r) => r.id === keyOf(platform, jobId));
}

/** Insert or merge a job record. Status changes are appended to history. */
export function upsert(platform, jobId, patch) {
  return withLock(() => upsertUnlocked(platform, jobId, patch));
}

function upsertUnlocked(platform, jobId, patch) {
  const rows = loadAll();
  const id = keyOf(platform, jobId);
  const now = new Date().toISOString();
  let row = rows.find((r) => r.id === id);
  if (!row) {
    row = { id, platform, jobId: String(jobId), foundAt: now, notes: "", history: [] };
    rows.unshift(row);
  }
  if (patch.status && patch.status !== row.status) {
    row.history.push({ at: now, status: patch.status, note: patch.historyNote ?? "" });
    if (patch.status === "applied" && !row.appliedAt) row.appliedAt = now;
  }
  const { historyNote, ...rest } = patch;
  Object.assign(row, rest, { updatedAt: now });
  saveAll(rows);
  return row;
}

export function update(id, patch) {
  const row = loadAll().find((r) => r.id === id);
  if (!row) return null;
  return upsert(row.platform, row.jobId, patch);
}

export function remove(id) {
  return withLock(() => {
    const rows = loadAll();
    const next = rows.filter((r) => r.id !== id);
    saveAll(next);
    return next.length !== rows.length;
  });
}

export function appliedToday() {
  const today = new Date().toDateString();
  return loadAll().filter((r) => r.appliedAt && new Date(r.appliedAt).toDateString() === today).length;
}
