// Starts/stops the agent as a child process of the dashboard server and relays its questions.
import { fork } from "node:child_process";
import path from "node:path";
import { ROOT } from "./util.mjs";

const MAX_LOG = 600;
const state = { running: false, startedAt: null, endedAt: null, exitCode: null, options: null, pending: null, log: [], seq: 0 };
let child = null;

const strip = (s) => s.replace(/\x1b\[[0-9;]*m/g, "").replace(/^\d{1,2}:\d{2}:\d{2}(\s?[AP]M)?\s/i, "");
function push(line, kind = "out") {
  if (!line.trim()) return;
  state.seq++;
  state.log.push({ n: state.seq, at: Date.now(), kind, text: strip(line) });
  if (state.log.length > MAX_LOG) state.log.splice(0, state.log.length - MAX_LOG);
}
function pipe(stream, kind) {
  let buf = "";
  stream.on("data", (d) => {
    buf += d;
    const lines = buf.split("\n");
    buf = lines.pop();
    lines.forEach((l) => push(l, kind));
  });
}

export function status(since = 0) {
  const { log, ...rest } = state;
  return { ...rest, log: log.filter((l) => l.n > since) };
}

export function start({ mode = "review", platform = "", max = 15 } = {}) {
  if (child) throw new Error("The agent is already running");
  if (!["review", "auto", "dry-run"].includes(mode)) throw new Error("Unknown mode");
  const args = [`--mode=${mode}`, `--max=${Math.max(1, Math.min(50, Number(max) || 15))}`];
  if (["linkedin", "naukri"].includes(platform)) args.push(`--platform=${platform}`);

  Object.assign(state, { running: true, startedAt: Date.now(), endedAt: null, exitCode: null, options: { mode, platform, max }, pending: null, log: [] });
  push(`▶ Starting agent (${args.join(" ")})`, "sys");
  child = fork(path.join(ROOT, "src", "agent.mjs"), args, { cwd: ROOT, stdio: ["ignore", "pipe", "pipe", "ipc"], env: { ...process.env, FORCE_COLOR: "0" } });
  pipe(child.stdout, "out");
  pipe(child.stderr, "err");
  child.on("message", (m) => {
    if (m?.type === "ask") {
      state.pending = { id: m.id, question: m.question, choices: m.choices ?? [], at: Date.now() };
      push(`? ${m.question}`, "ask");
    }
  });
  child.on("exit", (code, signal) => {
    push(signal ? `■ Agent stopped` : `■ Agent finished (exit code ${code})`, "sys");
    Object.assign(state, { running: false, endedAt: Date.now(), exitCode: code, pending: null });
    child = null;
  });
  return status();
}

export function stop() {
  if (!child) return status();
  push("■ Stop requested…", "sys");
  const c = child;
  c.kill("SIGTERM");
  setTimeout(() => c.exitCode === null && c.signalCode === null && c.kill("SIGKILL"), 8000);
  return status();
}

export function answer(id, value) {
  if (!child || !state.pending || state.pending.id !== id) throw new Error("No question is waiting for an answer");
  const label = state.pending.choices.find((c) => c.value === value)?.label ?? value;
  push(`→ ${label || "Continue"}`, "sys");
  child.send({ type: "answer", id, answer: value });
  state.pending = null;
  return status();
}

for (const sig of ["SIGINT", "SIGTERM"]) {
  process.on(sig, () => {
    child?.kill("SIGTERM");
    process.exit(0);
  });
}
