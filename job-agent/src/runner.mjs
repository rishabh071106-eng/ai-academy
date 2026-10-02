// Starts/stops one agent per platform (LinkedIn and Naukri run independently) and relays their questions.
import { fork } from "node:child_process";
import path from "node:path";
import { ROOT } from "./util.mjs";

export const PLATFORMS = ["linkedin", "naukri", "alignerr"];
const MAX_LOG = 600;
const runs = Object.fromEntries(PLATFORMS.map((p) => [p, { platform: p, running: false, startedAt: null, endedAt: null, exitCode: null, options: null, pending: null, log: [], seq: 0, child: null }]));

const strip = (s) => s.replace(/\x1b\[[0-9;]*m/g, "").replace(/^\d{1,2}:\d{2}:\d{2}(\s?[AP]M)?\s/i, "");
function push(run, line, kind = "out") {
  if (!line.trim()) return;
  run.seq++;
  run.log.push({ n: run.seq, at: Date.now(), kind, text: strip(line) });
  if (run.log.length > MAX_LOG) run.log.splice(0, run.log.length - MAX_LOG);
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
  const { child, log, stopRequested, ...rest } = run;
  return { ...rest, log: log.filter((l) => l.n > since) };
};
const get = (platform) => {
  const run = runs[platform];
  if (!run) throw new Error("Unknown platform");
  return run;
};

/** since = { linkedin: n, naukri: n } — only log lines newer than those are returned. */
export function status(since = {}) {
  return { runs: Object.fromEntries(PLATFORMS.map((p) => [p, view(runs[p], Number(since[p] || 0))])) };
}

export function start({ platform, mode = "review", max = 15, review = 0, keepGoing = true } = {}, restart = 0) {
  const run = get(platform);
  if (run.child) throw new Error(`The ${platform} agent is already running`);
  if (!["review", "auto", "dry-run"].includes(mode)) throw new Error("Unknown mode");
  max = Math.max(1, Math.min(500, Number(max) || 15));
  review = Math.max(0, Math.min(5000, Number(review) || 0));
  keepGoing = keepGoing !== false && keepGoing !== "false";
  const args = [`--platform=${platform}`, `--mode=${mode}`, `--max=${max}`, `--review=${review}`, `--keep-going=${keepGoing}`];

  if (!restart) Object.assign(run, { startedAt: Date.now(), log: [], restarts: 0 });
  Object.assign(run, { running: true, endedAt: null, exitCode: null, options: { mode, max, review, keepGoing }, pending: null, stopRequested: false });
  push(run, restart ? `↻ Restarting ${platform} agent after a crash (${restart}/5)` : `▶ Starting ${platform} agent (${mode}, apply to ${max}, review ${review || "all"}${keepGoing ? ", keep going" : ""})`, "sys");
  const child = fork(path.join(ROOT, "src", "agent.mjs"), args, { cwd: ROOT, stdio: ["ignore", "pipe", "pipe", "ipc"], env: { ...process.env, FORCE_COLOR: "0" } });
  run.child = child;
  pipe(run, child.stdout, "out");
  pipe(run, child.stderr, "err");
  child.on("message", (m) => {
    if (m?.type === "ask") {
      run.pending = { id: m.id, question: m.question, choices: m.choices ?? [], at: Date.now() };
      push(run, `? ${m.question}`, "ask");
    }
  });
  child.on("exit", (code, signal) => {
    // Exit code 3 = Claude API unusable (no credit / bad key): restarting won't help.
    const crashed = !run.stopRequested && code !== 3 && (code !== 0 || signal);
    Object.assign(run, { child: null, pending: null });
    // Keep-going runs come back by themselves after a crash (already-handled jobs are skipped).
    if (crashed && keepGoing && (run.restarts ?? 0) < 5) {
      run.restarts = (run.restarts ?? 0) + 1;
      push(run, `■ Agent stopped unexpectedly (exit ${code ?? signal}); restarting in 10 s…`, "err");
      setTimeout(() => { if (!run.stopRequested && !run.child) start(run.options && { platform, ...run.options }, run.restarts); }, 10000);
      return;
    }
    push(run, signal ? "■ Agent stopped" : code === 3 ? "■ Agent stopped: Claude API problem (see the line above)" : `■ Agent finished (exit code ${code})`, code === 3 ? "err" : "sys");
    run.fatal = code === 3 ? (run.log.filter((l) => /STOPPED:/.test(l.text)).at(-1)?.text.replace(/^.*STOPPED:\s*/, "") ?? "Claude API problem") : null;
    Object.assign(run, { running: false, endedAt: Date.now(), exitCode: code });
  });
  return status();
}

export function stop({ platform } = {}) {
  const run = get(platform);
  run.stopRequested = true;
  const c = run.child;
  if (!c) {
    if (run.running) Object.assign(run, { running: false, endedAt: Date.now() }); // was waiting to restart
    return status();
  }
  push(run, "■ Stop requested…", "sys");
  c.kill("SIGTERM");
  setTimeout(() => c.exitCode === null && c.signalCode === null && c.kill("SIGKILL"), 8000);
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
