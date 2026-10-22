// One place that talks to the AI model. config.provider picks it:
//   "gemini"    → Google Gemini API (GEMINI_API_KEY in .env)
//   "anthropic" → Claude API (ANTHROPIC_API_KEY in .env)
// Every caller asks for JSON that matches a schema, so both providers are used in
// structured-output mode and the result is parsed and returned as an object.
import fs from "node:fs";
import path from "node:path";
import { DATA_DIR, loadConfig, log, sleep, stopIfFatalApiError } from "./util.mjs";

const config = loadConfig();
const haveClaude = () => !!process.env.ANTHROPIC_API_KEY;
const haveGemini = () => !!process.env.GEMINI_API_KEY;
export const PROVIDER = (config.provider || (haveClaude() ? "anthropic" : "gemini")).toLowerCase();
// The provider in use; it can switch once during a run when the first one stops working
// (no credit, bad key) and the other key is in .env — the run carries on instead of stopping.
let provider = PROVIDER === "anthropic" && !haveClaude() && haveGemini() ? "gemini" : PROVIDER === "gemini" && !haveGemini() && haveClaude() ? "anthropic" : PROVIDER;
if (provider !== PROVIDER) log("warn", `No ${PROVIDER === "anthropic" ? "ANTHROPIC_API_KEY" : "GEMINI_API_KEY"} in .env — using ${provider === "gemini" ? "Gemini" : "Claude"} instead.`);
let switched = false;
function switchProvider(reason) {
  if (switched) return false;
  const other = provider === "gemini" ? "anthropic" : "gemini";
  if ((other === "gemini" && !haveGemini()) || (other === "anthropic" && !haveClaude())) return false;
  switched = true;
  provider = other;
  log("warn", `\n⚠ ${other === "gemini" ? "Claude" : "Gemini"} can't be used right now (${String(reason).split("\n")[0].slice(0, 120)}) — switching to ${other === "gemini" ? "Gemini" : "Claude"} for the rest of this run.`);
  return true;
}
export const currentProvider = () => provider;

/** The model for a role: "main" (matching, tailoring, answers) or "navigator" (click-by-click). */
export function modelFor(role = "main") {
  if (provider === "gemini") return (role === "navigator" && config.geminiNavigatorModel) || config.geminiModel || "gemini-flash-lite-latest";
  return (role === "navigator" && config.navigatorModel) || config.model || "claude-haiku-5-5";
}

/**
 * content: a string, or an array of { type: "text", text }, { type: "image", source: {…} } and
 * { type: "document", source: { type: "base64", media_type, data } } blocks (Claude block shapes).
 */
export async function generateJSON({ system, content, schema, effort = "medium", maxTokens = 16000, role = "main" }) {
  const args = { system, content, schema, effort, maxTokens, role };
  return provider === "gemini" ? gemini(args) : claude(args);
}

// ---------------------------------------------------------------- Claude
// claude-opus-5-5 with structured output (output_config.format json_schema), adaptive thinking
// (the model's default), explicit effort, and server-side refusal fallbacks.
let anthropic;
async function claude(args) {
  const { system, content, schema, effort, maxTokens, role } = args;
  if (!anthropic) {
    if (!haveClaude()) {
      if (switchProvider("ANTHROPIC_API_KEY is missing from .env")) return gemini(args);
      log("err", "\n■ STOPPED: ANTHROPIC_API_KEY is missing from job-agent/.env. Create a key at console.anthropic.com → API Keys, add it there, then press Start again.");
      process.exit(3);
    }
    const { default: Anthropic } = await import("@anthropic-ai/sdk");
    anthropic = new Anthropic();
  }
  for (let attempt = 1; ; attempt++) {
    let response;
    try {
      const model = modelFor(role);
      response = await anthropic.beta.messages.create({
        model,
        max_tokens: maxTokens,
        // Server-side refusal fallbacks exist for Opus/Sonnet/Fable; Haiku has none.
        ...(/haiku/i.test(model) ? {} : { betas: ["server-side-fallback-2026-07-01"], fallbacks: "default" }),
        system,
        output_config: { effort, format: { type: "json_schema", schema } },
        messages: [{ role: "user", content }],
      });
    } catch (e) {
      const status = e?.status ?? 0;
      const msg = String(e?.message ?? e);
      const fatal = status === 401 || status === 403 || /credit balance is too low|billing|purchase credits|invalid x-api-key|authentication_error|permission_error/i.test(msg);
      if (fatal) {
        if (switchProvider(msg)) return gemini(args);
        stopIfFatalApiError(e);
        throw e;
      }
      // Rate limit / overloaded / temporary: wait and retry a few times (the SDK already retried twice).
      if ([408, 409, 429, 500, 502, 503, 504, 529].includes(status) && attempt < 5) {
        const wait = Math.min(120, 10 * attempt);
        log("dim", `   Claude busy (${status}); retrying in ${wait} s…`);
        await sleep(wait * 1000);
        continue;
      }
      throw e;
    }
    if (response.stop_reason === "refusal") throw new Error(`Claude declined: ${response.stop_details?.explanation ?? "no explanation"}`);
    if (response.stop_reason === "max_tokens") throw new Error("Claude response was cut off (max_tokens)");
    return JSON.parse(response.content.filter((b) => b.type === "text").map((b) => b.text).join(""));
  }
}

/** A Gemini problem that would end the run: switch to Claude if its key is there, else stop. */
async function geminiGiveUp(message, args) {
  if (switchProvider(message)) return claude(args);
  log("err", `\n■ STOPPED: ${message}`);
  process.exit(3);
}

// ---------------------------------------------------------------- Gemini
// Two kinds of Google keys work:
//  - Google AI Studio keys ("AIza…")          → generativelanguage.googleapis.com
//  - Vertex AI express-mode keys ("AQ.…")     → aiplatform.googleapis.com
// A key may be restricted to one of the two services; if one says "blocked"/"not enabled",
// the other is tried and remembered for the rest of the run.
const ENDPOINTS = {
  studio: "https://generativelanguage.googleapis.com/v1beta",
  vertex: "https://aiplatform.googleapis.com/v1/publishers/google",
};
// Which Google service to call: config "geminiEndpoint" if set, else the one that worked last
// time (remembered in data/gemini-endpoint.txt), else the Gemini API (AI Studio) — that is
// where prepaid credits live, and it accepts both key types.
const ENDPOINT_MEMO = path.join(DATA_DIR, "gemini-endpoint.txt");
let endpoint = ["studio", "vertex"].includes(config.geminiEndpoint) ? config.geminiEndpoint : null;
if (!endpoint) {
  try {
    const saved = fs.readFileSync(ENDPOINT_MEMO, "utf8").trim();
    if (["studio", "vertex"].includes(saved)) endpoint = saved;
  } catch {}
}
endpoint ||= "studio";
const isVertexKey = () => endpoint === "vertex";
const geminiBase = () => process.env.GEMINI_BASE_URL || ENDPOINTS[endpoint];
let switchedEndpoint = false;
function rememberEndpoint() {
  try {
    fs.mkdirSync(DATA_DIR, { recursive: true });
    fs.writeFileSync(ENDPOINT_MEMO, endpoint);
  } catch {}
}

// If the configured model name isn't available for this key, try these in order.
const FALLBACK_MODELS = ["gemini-flash-lite-latest", "gemini-2.5-flash-lite", "gemini-flash-latest", "gemini-2.5-flash", "gemini-2.0-flash"];
let workingModel = null;

const toParts = (content) =>
  (typeof content === "string" ? [{ type: "text", text: content }] : content).map((b) =>
    b.type === "document" || b.type === "image" ? { inline_data: { mime_type: b.source.media_type, data: b.source.data } } : { text: b.text },
  );

// Older Gemini models only take the OpenAPI-style `responseSchema` (no additionalProperties).
function toOpenApiSchema(s) {
  if (Array.isArray(s)) return s.map(toOpenApiSchema);
  if (!s || typeof s !== "object") return s;
  const out = {};
  for (const [k, v] of Object.entries(s)) {
    if (k === "additionalProperties") continue;
    out[k] = k === "properties" ? Object.fromEntries(Object.entries(v).map(([pk, pv]) => [pk, toOpenApiSchema(pv)])) : toOpenApiSchema(v);
  }
  return out;
}

let schemaField = "responseJsonSchema";
async function gemini(args) {
  const { system, content, schema, maxTokens, role } = args;
  const key = process.env.GEMINI_API_KEY;
  if (!key) return geminiGiveUp("GEMINI_API_KEY is missing from job-agent/.env. Add it, then press Start again.", args);
  const wanted = modelFor(role);
  const candidates = [...new Set([workingModel && role === "main" ? workingModel : wanted, wanted, ...FALLBACK_MODELS].filter(Boolean))];
  let model = candidates.shift();
  for (let attempt = 1; ; attempt++) {
    const body = {
      systemInstruction: { parts: [{ text: system }] },
      contents: [{ role: "user", parts: toParts(content) }],
      generationConfig: {
        maxOutputTokens: Math.max(maxTokens, 8192),
        responseMimeType: "application/json",
        [schemaField]: schemaField === "responseJsonSchema" ? schema : toOpenApiSchema(schema),
      },
    };
    let res, data;
    try {
      res = await fetch(`${geminiBase()}/models/${encodeURIComponent(model)}:generateContent`, {
        method: "POST",
        headers: { "content-type": "application/json", "x-goog-api-key": key },
        body: JSON.stringify(body),
      });
      data = await res.json().catch(() => ({}));
    } catch (e) {
      if (attempt < 4) {
        await sleep(2000 * attempt);
        continue;
      }
      throw new Error(`Gemini unreachable: ${e.message}`);
    }
    if (res.ok) {
      if (role === "main") workingModel = model;
      if (switchedEndpoint) {
        rememberEndpoint();
        switchedEndpoint = false;
      }
      const cand = data.candidates?.[0];
      const text = (cand?.content?.parts || []).filter((p) => p.text && !p.thought).map((p) => p.text).join("");
      if (!text) throw new Error(`Gemini returned no answer (${cand?.finishReason || data.promptFeedback?.blockReason || "empty"})`);
      if (cand.finishReason === "MAX_TOKENS") throw new Error("Gemini response was cut off (max tokens)");
      return JSON.parse(text.replace(/^```(?:json)?\s*|\s*```$/g, ""));
    }
    const msg = data.error?.message || `HTTP ${res.status}`;
    // Model too old for responseJsonSchema: fall back to responseSchema once.
    if (res.status === 400 && schemaField === "responseJsonSchema" && /responseJsonSchema|response_json_schema|Unknown name/i.test(msg)) {
      schemaField = "responseSchema";
      continue;
    }
    if (/api key not valid|API_KEY_INVALID|api key expired/i.test(msg)) return geminiGiveUp(`The Gemini API key in job-agent/.env is not valid (tried ${isVertexKey() ? "Vertex AI" : "the Gemini API"}). Check it was copied completely, or create a new one, then press Start again.`, args);
    // Key not allowed on this Google service: try the other one once.
    if ((res.status === 403 || res.status === 401) && !switchedEndpoint && !process.env.GEMINI_BASE_URL && !config.geminiEndpoint) {
      switchedEndpoint = true;
      endpoint = endpoint === "vertex" ? "studio" : "vertex";
      log("dim", `   (using ${endpoint === "studio" ? "the Gemini API (AI Studio)" : "Vertex AI"} for this key)`);
      continue;
    }
    if (res.status === 402 || /credits are depleted|billing|payment required/i.test(msg)) return geminiGiveUp(`The Google account behind GEMINI_API_KEY has no credit left (${msg.split(".")[0]}). Add credits at https://ai.studio/projects, or put a new key from https://aistudio.google.com/apikey into job-agent/.env, then press Start again.`, args);
    if (res.status === 403) return geminiGiveUp(`Google refused the request on both of its Gemini services (${msg}). The simplest fix: create a key at aistudio.google.com/apikey and put it in .env as GEMINI_API_KEY.`, args);
    if (res.status === 404 && candidates.length) {
      log("dim", `   Gemini model "${model}" isn't available for this key; trying "${candidates[0]}"`);
      model = candidates.shift();
      continue;
    }
    if (res.status === 404) return geminiGiveUp(`Gemini model "${model}" not found. Set "geminiModel" in config.json to a current model (e.g. gemini-flash-latest).`, args);
    // Rate limits and temporary errors: wait and retry (Gemini says how long).
    if ([429, 500, 502, 503, 504].includes(res.status) && attempt < 6) {
      const hint = JSON.stringify(data.error?.details || []).match(/"retryDelay":"(\d+(?:\.\d+)?)s"/)?.[1];
      const wait = Math.min(120, hint ? Number(hint) + 1 : 5 * attempt);
      log("dim", `   Gemini busy (${res.status}); retrying in ${Math.round(wait)} s…`);
      await sleep(wait * 1000);
      continue;
    }
    if (res.status === 429) return geminiGiveUp("Your Gemini quota is used up for now (rate or daily limit). Wait, or raise the limit / enable billing in Google AI Studio, then press Start again.", args);
    throw new Error(`Gemini error ${res.status}: ${msg}`);
  }
}
