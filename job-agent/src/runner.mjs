// Starts/stops one agent per platform (LinkedIn and Naukri run independently) and relays their questions.
import { fork } from "node:child_process";
import path from "node:path";
import { ROOT } from "./util.mjs";

export const PLATFORMS = ["linkedin", "naukri"];
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
  const { child, log, ...rest } = run;
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

export function start({ platform, mode = "review", max = 15 } = {}) {
  const run = get(platform);
  if (run.child) throw new Error(`The ${platform} agent is already running`);
  if (!["review", "auto", "dry-run"].includes(mode)) throw new Error("Unknown mode");
  const args = [`--platform=${platform}`, `--mode=${mode}`, `--max=${Math.max(1, Math.min(50, Number(max) || 15))}`];

  Object.assign(run, { running: true, startedAt: Date.now(), endedAt: null, exitCode: null, options: { mode, max }, pending: null, log: [] });
  push(run, `▶ Starting ${platform} agent (${mode}, max ${max})`, "sys");
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
    push(run, signal ? "■ Agent stopped" : `■ Agent finished (exit code ${code})`, "sys");
    Object.assign(run, { running: false, endedAt: Date.now(), exitCode: code, pending: null, child: null });
  });
  return status();
}

export function stop({ platform } = {}) {
  const run = get(platform);
  const c = run.child;
  if (!c) return status();
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
