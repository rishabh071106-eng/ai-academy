// Local dashboard: http://localhost:4321  (data stays on this machine)
import fs from "node:fs";
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
    if (p === "/api/agent" && req.method === "GET") return send(res, 200, runner.status(Number(url.searchParams.get("since") || 0)));
    if (p === "/api/agent/start" && req.method === "POST") return send(res, 200, runner.start(await readBody(req)));
    if (p === "/api/agent/stop" && req.method === "POST") return send(res, 200, runner.stop());
    if (p === "/api/agent/answer" && req.method === "POST") {
      const b = await readBody(req);
      return send(res, 200, runner.answer(Number(b.id), String(b.answer ?? "")));
    }
  } catch (e) {
    return send(res, 409, { error: e.message });
  }
  if (p === "/api/profile") {
    const prof = readJson(path.join(ROOT, "profile.json"), {});
    return send(res, 200, { name: prof.name ?? "", headline: prof.headline ?? "" });
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
    if (b.status) patch.historyNote = "Updated on dashboard";
    const row = tracker.update(m[1], patch);
    return row ? send(res, 200, row) : send(res, 404, { error: "not found" });
  }
  if (m && req.method === "DELETE") return send(res, tracker.remove(m[1]) ? 200 : 404, {});
  send(res, 404, { error: "not found" });
});

server.listen(PORT, "127.0.0.1", () => log("ok", `Dashboard: http://localhost:${PORT}`));
