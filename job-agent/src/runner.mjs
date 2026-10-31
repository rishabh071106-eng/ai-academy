// Starts/stops one agent per platform (LinkedIn and Naukri run independently) and relays their questions.
import { fork } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { TIERS } from "./priority.mjs";
import { profileUpdates } from "./profile-update.mjs";
import { loadConfig, ROOT } from "./util.mjs";

const PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#8e5cd9", "#d6336c", "#0ca5b8", "#c27c0e", "#5c7cfa", "#2f9e44", "#e03131", "#f08c00", "#7048e8", "#1098ad", "#868e96", "#e64980", "#37b24d"];
const cfg0 = loadConfig();
const cfgPlatforms = cfg0.platforms ?? {};
export const PLATFORMS = Object.keys(cfgPlatforms).filter((k) => cfgPlatforms[k]?.enabled !== false);
export const LABELS = Object.fromEntries(PLATFORMS.map((k) => [k, cfgPlatforms[k].label || { linkedin: "LinkedIn", naukri: "Naukri" }[k] || k[0].toUpperCase() + k.slice(1)]));
/** [{ key, label, color, group, profileOnly, notes, needs }] for the dashboard. */
export const platformList = () => PLATFORMS.map((k, i) => ({ key: k, label: LABELS[k], color: PALETTE[i % PALETTE.length], group: cfgPlatforms[k].group || "", profileOnly: !!cfgPlatforms[k].profileOnly, notes: cfgPlatforms[k].notes || "", needs: cfgPlatforms[k].needs || "" }));
// With fifty sites, only maxConcurrentAgents (6) agents run at once: the others wait in a queue
// and take over as slots free up. Job agents that keep going give up their slot after
// rotateMinutes (40) and rejoin the end of the queue, so every site gets its turn.
export const MAX_CONCURRENT = Math.max(1, Number(process.env.JOB_AGENT_MAX_CONCURRENT || cfg0.maxConcurrentAgents || 6));
const ROTATE_MS = process.env.JOB_AGENT_ROTATE_MS ? Number(process.env.JOB_AGENT_ROTATE_MS) : Math.max(0, Number(cfg0.rotateMinutes ?? 40)) * 60000;
const AGENT_SCRIPT = process.env.JOB_AGENT_SCRIPT || path.join(ROOT, "src", "agent.mjs");
const MAX_LOG = 600;
const runs = Object.fromEntries(PLATFORMS.map((p) => [p, { platform: p, running: false, queued: false, slot: null, startedAt: null, endedAt: null, exitCode: null, options: null, pending: null, log: [], seq: 0, child: null }]));
const queue = []; // platform keys waiting for a slot, first in first out
const runningCount = () => Object.values(runs).filter((r) => r.child).length;
const freeSlot = () => {
  const used = new Set(Object.values(runs).filter((r) => r.child).map((r) => r.slot));
  for (let i = 0; i < MAX_CONCURRENT; i++) if (!used.has(i)) return i;
  return runningCount();
};

const strip = (s) => s.replace(/\x1b\[[0-9;]*m/g, "").replace(/^\d{1,2}:\d{2}:\d{2}(\s?[AP]M)?\s/i, "");
const LOG_DIR = path.join(ROOT, "data", "logs");
const dayStamp = (d = new Date()) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
function push(run, line, kind = "out") {
  if (!line.trim()) return;
  run.seq++;
  const text = strip(line);
  run.log.push({ n: run.seq, at: Date.now(), kind, text });
  if (run.log.length > MAX_LOG) run.log.splice(0, run.log.length - MAX_LOG);
  // Also on disk, so a whole day's run can be downloaded from the dashboard (⇩ Logs).
  try {
    fs.mkdirSync(LOG_DIR, { recursive: true });
    fs.appendFileSync(path.join(LOG_DIR, `${run.platform}-${dayStamp()}.log`), `${new Date().toLocaleTimeString()}  ${text}\n`);
  } catch {}
}

/** Today's (or `date`'s) logs of every agent plus a summary of where jobs got stuck, as text. */
export function logsText(date = dayStamp()) {
  const parts = [];
  try {
    const rows = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "applications.json"), "utf8"));
    const byStatus = {};
    for (const r of rows) byStatus[r.status] = (byStatus[r.status] ?? 0) + 1;
    parts.push(`JOB AGENT LOGS — ${date}\n\nJobs by status: ${Object.entries(byStatus).map(([k, v]) => `${k} ${v}`).join(" · ")}`);
    const stuck = rows.filter((r) => ["needs_attention", "unable", "external"].includes(r.status));
    const reasons = {};
    for (const r of stuck) {
      const why = (r.lastNote || r.history?.at(-1)?.note || "(no note)").replace(/https?:\S+/g, "").slice(0, 90);
      reasons[why] = (reasons[why] ?? 0) + 1;
    }
    parts.push(`\nWhy jobs are not applied yet (${stuck.length}):\n${Object.entries(reasons).sort((a, b) => b[1] - a[1]).map(([k, v]) => `  ${String(v).padStart(3)} × ${k}`).join("\n")}`);
    const today = rows.filter((r) => (r.updatedAt || "").startsWith(date));
    parts.push(`\nJobs touched on ${date} (${today.length}):\n${today.map((r) => `  [${r.platform}] ${r.status.padEnd(16)} ${(r.title || "").slice(0, 50).padEnd(50)} ${(r.company || "").slice(0, 28).padEnd(28)} ${(r.lastNote || "").replace(/https?:\S+/g, "").slice(0, 100)}`).join("\n")}`);
  } catch (e) {
    parts.push(`(no tracker summary: ${e.message})`);
  }
  for (const p of PLATFORMS) {
    const file = path.join(LOG_DIR, `${p}-${date}.log`);
    parts.push(`\n\n===== ${p.toUpperCase()} AGENT =====\n${fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "(no log for this day)"}`);
  }
  return parts.join("\n");
}
function pipe(run, stream, kind) {
  let buf = "";
  stream.on("data", (d) => {
    buf += d;
    const lines = buf.split("\n");
    buf = lines.pop();
    lines.forEach((l) => push(run, l, kind));
  });
}
const view = (run, since = 0) => {
  const { child, log, stopRequested, rotating, ...rest } = run;
  return { ...rest, queuePos: run.queued ? queue.indexOf(run.platform) + 1 : 0, log: log.filter((l) => l.n > since) };
};
const get = (platform) => {
  const run = runs[platform];
  if (!run) throw new Error("Unknown platform");
  return run;
};

/** since = { linkedin: n, naukri: n } — only log lines newer than those are returned. */
export function status(since = {}) {
  return { platforms: platformList(), tiers: TIERS.map((t) => ({ name: t.name, keywords: t.keywords })), profiles: profileUpdates(), maxConcurrent: MAX_CONCURRENT, rotateMinutes: ROTATE_MS / 60000, queue: [...queue], runs: Object.fromEntries(PLATFORMS.map((p) => [p, view(runs[p], Number(since[p] || 0))])) };
}

export function start({ platform, mode = "review", max = 15, review = 0, keepGoing = true, retry = true, task = "jobs" } = {}, restart = 0) {
  const run = get(platform);
  if (run.child) throw new Error(`The ${platform} agent is already running`);
  if (run.queued) throw new Error(`The ${platform} agent is already waiting in the queue`);
  if (!["review", "auto", "dry-run"].includes(mode)) throw new Error("Unknown mode");
  max = Math.max(1, Math.min(2000, Number(max) || 1000));
  review = Math.max(0, Math.min(5000, Number(review) || 0));
  keepGoing = keepGoing !== false && keepGoing !== "false";
  retry = retry !== false && retry !== "false" && !restart; // a crash-restart doesn't redo the retry pass
  if (task === "profile") keepGoing = false; // one pass, then the agent exits
  const options = { mode, max, review, keepGoing, retry, task };
  if (!restart) Object.assign(run, { log: [], restarts: 0, fatal: null, stopRequested: false });
  if (!restart && runningCount() >= MAX_CONCURRENT) {
    enqueue(run, options, `⏳ Waiting for a turn (${queue.length + 1} in the queue): ${MAX_CONCURRENT} agents run at a time${ROTATE_MS ? `, each job agent gets ${ROTATE_MS / 60000} min before the next site takes over` : ""}`);
    return status();
  }
  launch(platform, options, restart);
  return status();
}

function enqueue(run, options, message) {
  Object.assign(run, { queued: true, running: false, options, pending: null, endedAt: null, stopRequested: false, rotating: false });
  queue.push(run.platform);
  push(run, message, "sys");
}

/** Starts queued agents while there are free slots. */
function pump() {
  while (queue.length && runningCount() < MAX_CONCURRENT) {
    const run = runs[queue.shift()];
    run.queued = false;
    if (run.stopRequested) continue;
    launch(run.platform, run.options, 0);
  }
}

/** A long-running job agent hands its slot to the next site in the queue after rotateMinutes. */
function rotate() {
  if (!ROTATE_MS || !queue.some((k) => !runs[k].stopRequested)) return;
  const due = Object.values(runs)
    .filter((r) => r.child && !r.rotating && !r.stopRequested && r.options?.task !== "profile" && r.options?.keepGoing && !r.pending && Date.now() - (r.startedAt || 0) >= ROTATE_MS)
    .sort((a, b) => a.startedAt - b.startedAt)[0];
  if (!due) return;
  due.rotating = true;
  due.stopRequested = true;
  push(due, `⟳ Pausing after ${Math.round((Date.now() - due.startedAt) / 60000)} min so a waiting site gets a turn; it rejoins the queue and carries on later`, "sys");
  const c = due.child;
  c.kill("SIGTERM");
  setTimeout(() => c.exitCode === null && c.signalCode === null && c.kill("SIGKILL"), 60000);
}
const rotateTimer = setInterval(rotate, Number(process.env.JOB_AGENT_ROTATE_TICK_MS) || 60000);
rotateTimer.unref?.();

function launch(platform, { mode, max, review, keepGoing, retry, task }, restart = 0) {
  const run = get(platform);
  const slot = freeSlot();
  const args = [`--platform=${platform}`, `--mode=${mode}`, `--max=${max}`, `--review=${review}`, `--keep-going=${keepGoing}`, `--retry=${retry}`, `--task=${task}`, `--slot=${slot}`, `--slots=${MAX_CONCURRENT}`];
  if (!restart) run.startedAt = Date.now();
  Object.assign(run, { running: true, queued: false, slot, endedAt: null, exitCode: null, options: { mode, max, review, keepGoing, retry, task }, pending: null, stopRequested: false, rotating: false });
  push(run, restart ? `↻ Restarting ${platform} agent after a crash (${restart}/5)` : task === "profile" ? `↻ Updating her ${platform} profile from the resume…` : `▶ Starting ${platform} agent (${mode}, apply to ${max}, review ${review || "all"}${keepGoing ? ", keep going" : ""})`, "sys");
  const child = fork(AGENT_SCRIPT, args, { cwd: ROOT, stdio: ["ignore", "pipe", "pipe", "ipc"], env: { ...process.env, FORCE_COLOR: "0" } });
  run.child = child;
  pipe(run, child.stdout, "out");
  pipe(run, child.stderr, "err");
  child.on("message", (m) => {
    if (m?.type === "ask") {
      run.pending = { id: m.id, question: m.question, choices: m.choices ?? [], at: Date.now(), timeoutMs: m.timeoutMs || 0 };
      push(run, `? ${m.question}`, "ask");
    }
    if (m?.type === "job") run.current = m.title ? { title: m.title, company: m.company || "", url: m.url || "", tier: m.tier || "", matchScore: m.matchScore ?? null, at: Date.now() } : null;
    if (m?.type === "ask-timeout" && run.pending?.id === m.id) {
      push(run, m.skipped ? "→ skipped by you" : "→ no answer in time; skipped", "sys");
      run.pending = null;
      }
  });
  child.on("exit", (code, signal) => {
    const rotating = run.rotating;
    // Exit code 3 = Claude API unusable (no credit / bad key): restarting won't help.
    const crashed = !run.stopRequested && !rotating && code !== 3 && (code !== 0 || signal);
    Object.assign(run, { child: null, pending: null, current: null, slot: null, rotating: false });
    // Keep-going runs come back by themselves after a crash (already-handled jobs are skipped).
    if (crashed && keepGoing && (run.restarts ?? 0) < 5) {
      run.restarts = (run.restarts ?? 0) + 1;
      push(run, `■ Agent stopped unexpectedly (exit ${code ?? signal}); restarting in 10 s…`, "err");
      setTimeout(() => { if (!run.stopRequested && !run.child && !run.queued) launch(platform, run.options, run.restarts); }, 10000);
      return;
    }
    push(run, rotating ? "⟳ Paused for the next site" : signal ? "■ Agent stopped" : code === 3 ? "■ Agent stopped (see the line above)" : `■ Agent finished (exit code ${code})`, code === 3 ? "err" : "sys");
    run.fatal = code === 3 ? (run.log.filter((l) => /STOPPED:/.test(l.text)).at(-1)?.text.replace(/^.*STOPPED:\s*/, "") ?? "see the live log") : null;
    Object.assign(run, { running: false, endedAt: Date.now(), exitCode: code });
    if (rotating) enqueue(run, run.options, `⏳ Back in the queue (${queue.length + 1} waiting); it continues where it left off`);
    pump();
  });
}

export function stop({ platform } = {}) {
  if (platform === "all") {
    for (const k of [...queue]) stop({ platform: k });
    for (const r of Object.values(runs)) if (r.child || r.running) stop({ platform: r.platform });
    return status();
  }
  const run = get(platform);
  run.stopRequested = true;
  run.rotating = false; // a stop by you is final: no rejoining the queue
  if (run.queued) {
    queue.splice(queue.indexOf(platform), 1);
    Object.assign(run, { queued: false, running: false, endedAt: Date.now() });
    push(run, "■ Taken out of the queue", "sys");
    return status();
  }
  const c = run.child;
  if (!c) {
    if (run.running) Object.assign(run, { running: false, endedAt: Date.now() }); // was waiting to restart
    return status();
  }
  push(run, "■ Stop requested…", "sys");
  c.kill("SIGTERM");
  // The agent first puts her own resume back on Naukri; give it up to a minute.
  setTimeout(() => c.exitCode === null && c.signalCode === null && c.kill("SIGKILL"), 60000);
  return status();
}

/** "Skip this job": the agent drops the job it's working on and moves to the next one. */
export function skip({ platform } = {}) {
  const run = get(platform);
  if (!run.child) throw new Error(`The ${platform} agent isn't running`);
  push(run, `⏭ Skip ${run.current?.title ? `"${run.current.title}"` : "this job"} (asked by you)`, "sys");
  run.child.send({ type: "skip" });
  return status();
}


export function answer({ platform, id, answer: value = "" } = {}) {
  const run = get(platform);
  if (!run.child || !run.pending || run.pending.id !== Number(id)) throw new Error("No question is waiting for an answer");
  const label = run.pending.choices.find((c) => c.value === value)?.label ?? value;
  push(run, `→ ${label || "Continue"}`, "sys");
  run.child.send({ type: "answer", id: Number(id), answer: String(value) });
  run.pending = null;
  return status();
}

for (const sig of ["SIGINT", "SIGTERM"]) {
  process.on(sig, () => {
    for (const r of Object.values(runs)) r.child?.kill("SIGTERM");
    process.exit(0);
  });
}
