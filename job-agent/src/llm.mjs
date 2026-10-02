import Anthropic from "@anthropic-ai/sdk";
import { loadConfig } from "./util.mjs";

const client = new Anthropic();
const MODEL = loadConfig().model || "claude-opus-5-5";

const obj = (properties) => ({
  type: "object",
  properties,
  required: Object.keys(properties),
  additionalProperties: false,
});
const str = { type: "string" };
const strArr = { type: "array", items: str };

/** One Claude call that must return JSON matching `schema`. */
async function jsonCall({ system, content, schema, effort = "medium", maxTokens = 16000 }) {
  const response = await client.beta.messages.create({
    model: MODEL,
    max_tokens: maxTokens,
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    system,
    output_config: { effort, format: { type: "json_schema", schema } },
    messages: [{ role: "user", content }],
  });
  if (response.stop_reason === "refusal") {
    throw new Error(`Claude declined: ${response.stop_details?.explanation ?? "no explanation"}`);
  }
  if (response.stop_reason === "max_tokens") throw new Error("Claude response was cut off (max_tokens)");
  const text = response.content.filter((b) => b.type === "text").map((b) => b.text).join("");
  return JSON.parse(text);
}

const HONESTY_RULES = `Hard rules:
- Never invent employers, dates, projects, degrees, certifications, numbers or skills the candidate does not have.
- You may reorder, rephrase, emphasise and trim existing facts, and mirror the job description's wording where it truthfully describes the candidate's work.
- Keep it to what fits on 1-2 A4 pages.`;

const EVAL_SCHEMA = obj({
  matchScore: { type: "integer", description: "0-100 fit of candidate to this job" },
  shouldApply: { type: "boolean" },
  matchReasons: { ...strArr, description: "2-4 short reasons it fits" },
  missingSkills: { ...strArr, description: "Required skills the candidate lacks" },
  tailored: obj({
    headline: str,
    summary: str,
    skills: { ...strArr, description: "12-20 skills, most relevant to this job first, only ones the candidate has" },
    experience: {
      type: "array",
      items: obj({ company: str, role: str, location: str, start: str, end: str, bullets: strArr }),
    },
  }),
  coverNote: { ...strArr, description: "Unused if empty" },
});

/** Score a job against the profile and, if it fits, produce resume content tailored to it. */
export async function evaluateAndTailor(profile, job) {
  const { applicationAnswers, ...resume } = profile;
  const result = await jsonCall({
    effort: "medium",
    schema: EVAL_SCHEMA,
    system: `You are a careful technical recruiter and resume writer. You decide whether a candidate should apply to a job and tailor their resume to it.
Scoring: 85+ = strong fit on core stack and seniority; 70-84 = good fit with minor gaps; below 70 = core stack or seniority mismatch.
Set shouldApply=false when the job's core technology is something the candidate has not used, or the role is clearly far more senior/junior.
${HONESTY_RULES}
For coverNote return 3-5 short sentences (as array items) for a recruiter message, or an empty array.
Return every experience entry from the candidate's profile (same companies, roles and dates), with bullets rewritten/reordered for this job; older roles can have fewer bullets.`,
    content: `CANDIDATE PROFILE (JSON):
${JSON.stringify(resume, null, 2)}

JOB:
Title: ${job.title}
Company: ${job.company}
Location: ${job.location ?? ""}
Description:
${(job.description ?? "").slice(0, 15000)}`,
  });
  return result;
}

const ANSWER_SCHEMA = obj({
  answers: {
    type: "array",
    items: obj({
      key: str,
      answer: { type: "string", description: "Exact value to enter, or exactly __ASK__ if it cannot be answered truthfully from the data" },
    }),
  },
});

/**
 * Answer application-form / chatbot screening questions.
 * fields: [{ key, label, type, options? }]. Returns { [key]: answer|"__ASK__" }.
 */
export async function answerQuestions(profile, job, fields) {
  if (!fields.length) return {};
  const { answers } = await jsonCall({
    effort: "low",
    maxTokens: 8000,
    schema: ANSWER_SCHEMA,
    system: `You fill job application screening questions on behalf of a candidate, using only the candidate data provided.
- For select/radio fields, answer with one of the given options, copied exactly.
- For "years of experience with X" give a whole number: use skillYears, or for related skills the closest sensible value; use 0 only when the candidate truly lacks it.
- For numeric fields answer digits only. CTC values are in lakhs per annum (LPA) unless the question asks for another unit; convert if needed.
- If a needed value is missing or starts with "TODO", or the question asks for something you cannot know (e.g. a personal opinion essay, reference names, ID numbers), answer exactly __ASK__.
- Never claim skills, degrees or legal statuses the data does not support.`,
    content: `CANDIDATE DATA:
${JSON.stringify(profile, null, 2)}

JOB: ${job.title} at ${job.company}

QUESTIONS (JSON):
${JSON.stringify(fields, null, 2)}`,
  });
  return Object.fromEntries(answers.map((a) => [a.key, a.answer]));
}

const PROFILE_SCHEMA = obj({
  name: str, headline: str, email: str, phone: str, city: str, address: str, linkedinUrl: str,
  totalExperienceYears: { type: "integer" },
  summary: str,
  skills: strArr,
  experience: {
    type: "array",
    items: obj({ company: str, role: str, location: str, start: str, end: str, bullets: strArr }),
  },
  education: { type: "array", items: obj({ degree: str, institution: str, start: str, end: str }) },
  certifications: { type: "array", items: obj({ name: str, date: str }) },
});

/** Turn a resume PDF into a profile.json skeleton. */
export async function extractProfile(pdfBase64) {
  return jsonCall({
    effort: "low",
    schema: PROFILE_SCHEMA,
    system: "Extract the resume into the JSON schema exactly as written. Do not embellish. Use YYYY-MM for dates and 'present' for current roles. Use empty strings for missing fields.",
    content: [
      { type: "document", source: { type: "base64", media_type: "application/pdf", data: pdfBase64 } },
      { type: "text", text: "Extract this resume." },
    ],
  });
}
