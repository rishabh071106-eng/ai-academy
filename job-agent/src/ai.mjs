// One place that talks to the AI model. config.provider picks it:
//   "gemini"    → Google Gemini API (GEMINI_API_KEY in .env)
//   "anthropic" → Claude API (ANTHROPIC_API_KEY in .env)
// Every caller asks for JSON that matches a schema, so both providers are used in
// structured-output mode and the result is parsed and returned as an object.
import { loadConfig, log, sleep, stopIfFatalApiError } from "./util.mjs";

const config = loadConfig();
export const PROVIDER = (config.provider || (process.env.GEMINI_API_KEY ? "gemini" : "anthropic")).toLowerCase();

/** The model for a role: "main" (matching, tailoring, answers) or "navigator" (click-by-click). */
export function modelFor(role = "main") {
  if (PROVIDER === "gemini") return (role === "navigator" && config.geminiNavigatorModel) || config.geminiModel || "gemini-flash-latest";
  return (role === "navigator" && config.navigatorModel) || config.model || "claude-opus-5-5";
}

/**
 * content: a string, or an array of { type: "text", text } and
 * { type: "document", source: { type: "base64", media_type, data } } blocks.
 */
export async function generateJSON({ system, content, schema, effort = "medium", maxTokens = 16000, role = "main" }) {
  return PROVIDER === "gemini" ? gemini({ system, content, schema, maxTokens, role }) : claude({ system, content, schema, effort, maxTokens, role });
}

// ---------------------------------------------------------------- Claude
let anthropic;
async function claude({ system, content, schema, effort, maxTokens, role }) {
  if (!anthropic) {
    const { default: Anthropic } = await import("@anthropic-ai/sdk");
    anthropic = new Anthropic();
  }
  const response = await anthropic.beta.messages
    .create({
      model: modelFor(role),
      max_tokens: maxTokens,
      betas: ["server-side-fallback-2026-07-01"],
      fallbacks: "default",
      system,
      output_config: { effort, format: { type: "json_schema", schema } },
      messages: [{ role: "user", content }],
    })
    .catch((e) => {
      stopIfFatalApiError(e);
      throw e;
    });
  if (response.stop_reason === "refusal") throw new Error(`Claude declined: ${response.stop_details?.explanation ?? "no explanation"}`);
  if (response.stop_reason === "max_tokens") throw new Error("Claude response was cut off (max_tokens)");
  return JSON.parse(response.content.filter((b) => b.type === "text").map((b) => b.text).join(""));
}

// ---------------------------------------------------------------- Gemini
// Two kinds of Google keys work:
//  - Google AI Studio keys ("AIza…")          → generativelanguage.googleapis.com
//  - Vertex AI express-mode keys ("AQ.…")     → aiplatform.googleapis.com
const isVertexKey = (key) => /^AQ\./.test(key) || config.geminiEndpoint === "vertex";
const geminiBase = (key) =>
  process.env.GEMINI_BASE_URL ||
  (isVertexKey(key) ? "https://aiplatform.googleapis.com/v1/publishers/google" : "https://generativelanguage.googleapis.com/v1beta");

// If the configured model name isn't available for this key, try these in order.
const FALLBACK_MODELS = ["gemini-flash-latest", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"];
let workingModel = null;

const toParts = (content) =>
  (typeof content === "string" ? [{ type: "text", text: content }] : content).map((b) =>
    b.type === "document" ? { inline_data: { mime_type: b.source.media_type, data: b.source.data } } : { text: b.text },
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
async function gemini({ system, content, schema, maxTokens, role }) {
  const key = process.env.GEMINI_API_KEY;
  if (!key) {
    log("err", "\n■ STOPPED: GEMINI_API_KEY is missing from job-agent/.env. Add it, then press Start again.");
    process.exit(3);
  }
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
      res = await fetch(`${geminiBase(key)}/models/${encodeURIComponent(model)}:generateContent`, {
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
    if (/api key not valid|API_KEY_INVALID|api key expired/i.test(msg)) {
      log("err", `\n■ STOPPED: The Gemini API key in job-agent/.env is not valid (${isVertexKey(key) ? "Vertex AI key" : "AI Studio key"}). Check it was copied completely, or create a new one, then press Start again.`);
      process.exit(3);
    }
    if (res.status === 403) {
      log("err", `\n■ STOPPED: Google refused the request (${msg}). ${isVertexKey(key) ? "For a Vertex AI key, the Vertex AI API must be enabled in its Google Cloud project." : "Check the key's project has the Gemini API enabled."}`);
      process.exit(3);
    }
    if (res.status === 404 && candidates.length) {
      log("dim", `   Gemini model "${model}" isn't available for this key; trying "${candidates[0]}"`);
      model = candidates.shift();
      continue;
    }
    if (res.status === 404) {
      log("err", `\n■ STOPPED: Gemini model "${model}" not found. Set "geminiModel" in config.json to a current model (e.g. gemini-flash-latest).`);
      process.exit(3);
    }
    // Rate limits and temporary errors: wait and retry (Gemini says how long).
    if ([429, 500, 502, 503, 504].includes(res.status) && attempt < 6) {
      const hint = JSON.stringify(data.error?.details || []).match(/"retryDelay":"(\d+(?:\.\d+)?)s"/)?.[1];
      const wait = Math.min(120, hint ? Number(hint) + 1 : 5 * attempt);
      log("dim", `   Gemini busy (${res.status}); retrying in ${Math.round(wait)} s…`);
      await sleep(wait * 1000);
      continue;
    }
    if (res.status === 429) {
      log("err", "\n■ STOPPED: Your Gemini quota is used up for now (rate or daily limit). Wait, or raise the limit / enable billing in Google AI Studio, then press Start again.");
      process.exit(3);
    }
    throw new Error(`Gemini error ${res.status}: ${msg}`);
  }
}
