// npm run check — one small AI call, and a plain report of which provider, model and key were used.
import { currentProvider, generateJSON, modelFor } from "./ai.mjs";
import { log } from "./util.mjs";

const key = process.env.GEMINI_API_KEY || "";
const mask = (k) => (k ? `${k.slice(0, 6)}…${k.slice(-4)} (${k.length} chars)` : "none");
log("info", `Provider: ${currentProvider()} · model: ${modelFor("main")}`);
log("info", `GEMINI_API_KEY: ${mask(key)}${key ? (/^AQ\./.test(key) ? " — Vertex-style key, sent to the Gemini API (AI Studio)" : /^AIza/.test(key) ? " — AI Studio key" : " — unrecognised format") : ""}`);
log("info", `ANTHROPIC_API_KEY: ${mask(process.env.ANTHROPIC_API_KEY || "")}`);
const t0 = Date.now();
try {
  const r = await generateJSON({ system: "Reply in JSON.", content: "Say hi and name the model family you are.", schema: { type: "object", properties: { msg: { type: "string" } }, required: ["msg"], additionalProperties: false }, effort: "low", maxTokens: 200 });
  log("ok", `OK in ${Date.now() - t0} ms via ${currentProvider()} / ${modelFor("main")}: ${JSON.stringify(r)}`);
  log("info", "The agents will use exactly this. If the provider shown isn't the one you paid for, check .env.");
} catch (e) {
  log("err", `FAILED: ${e.message.split("\n")[0]}`);
  process.exit(1);
}
process.exit(0);
