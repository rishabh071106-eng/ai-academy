// Local dashboard: http://localhost:4321  (data stays on this machine)
import fs from "node:fs";
import { execSync, fork } from "node:child_process";
import http from "node:http";
import path from "node:path";
import { DATA_DIR, ROOT, log, readJson } from "./util.mjs";
import * as runner from "./runner.mjs";
import * as tracker from "./tracker.mjs";

const PORT = Number(process.env.DASHBOARD_PORT || 4321);
const TYPES = { ".html": "text/html; charset=utf-8", ".pdf": "application/pdf", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml" };

const send = (res, code, body, type = "application/json") => {
  res.writeHead(code, { "Content-Type": type, "Cache-Control": "no-store" });
  res.end(typeof body === "string" || Buffer.isBuffer(body) ? body : JSON.stringify(body));
};
const readBody = (req) => new Promise((resolve) => {
  let b = "";
  req.on("data", (c) => (b += c));
  req.on("end", () => { try { resolve(JSON.parse(b || "{}")); } catch { resolve({}); } });
});

function serveFile(res, base, rel) {
  const file = path.resolve(base, rel);
  if (!file.startsWith(base + path.sep) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) return send(res, 404, { error: "not found" });
  send(res, 200, fs.readFileSync(file), TYPES[path.extname(file)] ?? "application/octet-stream");
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://localhost");
  const p = decodeURIComponent(url.pathname);

  if (p === "/" || p === "/index.html") return serveFile(res, path.join(ROOT, "dashboard"), "index.html");
  if (p.startsWith("/files/")) return serveFile(res, DATA_DIR, p.slice("/files/".length));

  try {
    if (p === "/api/agent" && req.method === "GET") return send(res, 200, runner.status(Object.fromEntries(url.searchParams)));
    if (p === "/api/agent/start" && req.method === "POST") return send(res, 200, runner.start(await readBody(req)));
    if (p === "/api/agent/stop" && req.method === "POST") return send(res, 200, runner.stop(await readBody(req)));
    if (p === "/api/agent/answer" && req.method === "POST") return send(res, 200, runner.answer(await readBody(req)));
  } catch (e) {
    return send(res, 409, { error: e.message });
  }
  if (p === "/api/profile") {
    const prof = readJson(path.join(ROOT, "profile.json"), {});
    return send(res, 200, { name: prof.name ?? "", headline: prof.headline ?? "", sourceResume: prof.sourceResume ?? null });
  }
  if (p === "/api/applications" && req.method === "GET") return send(res, 200, { statuses: tracker.STATUSES, rows: tracker.loadAll() });
  if (p === "/api/applications" && req.method === "POST") {
    const b = await readBody(req);
    if (!b.title || !b.company) return send(res, 400, { error: "title and company are required" });
    const row = tracker.upsert(b.platform || "other", b.jobId || `manual-${Date.now()}`, {
      title: b.title, company: b.company, url: b.url || "", location: b.location || "", status: b.status || "applied", notes: b.notes || "",
      historyNote: "Added manually",
    });
    return send(res, 201, row);
  }
  const m = p.match(/^\/api\/applications\/(.+)$/);
  if (m && req.method === "PATCH") {
    const b = await readBody(req);
    const patch = {};
    if (b.status && tracker.STATUSES.includes(b.status)) patch.status = b.status;
    if (typeof b.notes === "string") patch.notes = b.notes;
    if (b.hiringMessage && typeof b.hiringMessage.full === "string") {
      const cur = tracker.loadAll().find((r) => r.id === m[1])?.hiringMessage ?? {};
      patch.hiringMessage = { ...cur, ...b.hiringMessage };
    }
    if (b.status) patch.historyNote = "Updated on dashboard";
    const row = tracker.update(m[1], patch);
    return row ? send(res, 200, row) : send(res, 404, { error: "not found" });
  }
  const sm = p.match(/^\/api\/applications\/(.+)\/send-message$/);
  if (sm && req.method === "POST") {
    const child = fork(path.join(ROOT, "src", "send-message.mjs"), [sm[1]], { cwd: ROOT, stdio: ["ignore", "pipe", "pipe", "ipc"] });
    let out = "";
    child.stdout.on("data", (d) => (out += d));
    const timer = setTimeout(() => child.kill("SIGKILL"), 120000);
    child.on("exit", () => {
      clearTimeout(timer);
      const last = out.trim().split("\n").reverse().find((l) => l.startsWith("{"));
      let result = { status: "draft", note: "Sending failed" };
      try { if (last) result = JSON.parse(last); } catch {}
      send(res, 200, { result, row: tracker.loadAll().find((r) => r.id === sm[1]) });
    });
    return;
  }
  if (m && req.method === "DELETE") return send(res, tracker.remove(m[1]) ? 200 : 404, {});
  send(res, 404, { error: "not found" });
});

// If an older dashboard is still running (e.g. in another Terminal window), replace it
// so `git pull && npm run dashboard` always serves the new version.
let replaced = false;
let retries = 0;
server.on("error", (e) => {
  // The old dashboard may need a few seconds to shut down (it stops its agents first).
  if (e.code === "EADDRINUSE" && replaced && retries < 10) {
    retries++;
    setTimeout(() => server.listen(PORT, "127.0.0.1"), 1000);
    return;
  }
  if (e.code !== "EADDRINUSE" || replaced) {
    log("err", e.code === "EADDRINUSE" ? `Port ${PORT} is still in use. Close the other dashboard window (or run: lsof -ti tcp:${PORT} | xargs kill) and try again.` : e.message);
    process.exit(1);
  }
  replaced = true;
  let pids = [];
  try {
    pids = execSync(`lsof -ti tcp:${PORT} -sTCP:LISTEN`).toString().trim().split(/\s+/).filter(Boolean);
  } catch {}
  const ours = pids.filter((pid) => {
    try {
      return /src\/server\.mjs/.test(execSync(`ps -p ${pid} -o command=`).toString());
    } catch {
      return false;
    }
  });
  if (!ours.length) {
    log("err", `Port ${PORT} is used by another program. Set DASHBOARD_PORT in .env to a different number.`);
    process.exit(1);
  }
  log("warn", "An older dashboard was still running; replacing it with this one (any agent it was running is stopped)…");
  ours.forEach((pid) => { try { process.kill(Number(pid), "SIGTERM"); } catch {} });
  setTimeout(() => server.listen(PORT, "127.0.0.1"), 1500);
});
server.on("listening", () => log("ok", `Dashboard: http://localhost:${PORT}`));
server.listen(PORT, "127.0.0.1");
