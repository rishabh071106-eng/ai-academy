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
  jobTitle: { type: "string", description: "The job's title as stated on the page" },
  company: { type: "string", description: "Hiring company name as stated on the page" },
  location: { type: "string", description: "Job location, or empty" },
  descriptionComplete: { type: "boolean", description: "false if the job description looks cut off (ends mid-sentence, '…more', only a teaser)" },
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
  hiringMessage: obj({
    subject: { type: "string", description: "Short subject line for an InMail/email" },
    short: { type: "string", description: "Connection-request note, at most 280 characters" },
    full: { type: "string", description: "Message to the hiring manager/recruiter, 70-130 words" },
  }),
});

/** Score a job against the profile and, if it fits, produce resume content and a hiring-team message for it. */
export async function evaluateAndTailor(profile, job) {
  const { applicationAnswers = {}, ...resume } = profile;
  const contact = job.hiringContact?.name ? `${job.hiringContact.name}${job.hiringContact.title ? ` (${job.hiringContact.title})` : ""}` : "unknown";
  const result = await jsonCall({
    effort: "medium",
    schema: EVAL_SCHEMA,
    system: `You are a careful technical recruiter and resume writer. You decide whether a candidate should apply to a job, tailor their resume to it, and write a short message to the hiring team.

The candidate is a FULL-STACK engineer: back end (Adobe Commerce/Magento 2, PHP, MySQL, GraphQL, REST, RabbitMQ) AND front end (Next.js, React, TypeScript, JavaScript, HTML/CSS). Judge fit generously across both halves:
- Any role whose stack includes Magento/Adobe Commerce, React, Next.js, PHP or general e-commerce web development is a fit, whether it is titled front-end, back-end, full-stack, e-commerce, platform or "software engineer".
- Nice-to-have or secondary skills she lacks (e.g. Hyva, AWS, Docker, Vue, Node) lower the score a little but never make shouldApply false.
- Seniority: she has 9+ years. Senior, Lead, Staff and mid-level (4+ yrs) roles are all fine; Architect/Manager roles are fine if hands-on.
- shouldApply=false ONLY when the core stack is unrelated (e.g. Java/Spring-only, .NET, Python/data science, native iOS/Android, SAP, Salesforce, QA-only, DevOps-only) or the role is not a developer role.
The job text may be a raw copy of the whole web page (navigation, other job titles, ads). Find the actual job being viewed and judge only that; fill jobTitle/company/location from it.
Scoring: 85+ = core stack match; 70-84 = solid fit with some gaps; 55-69 = adjacent but workable; below 55 = unrelated.

${HONESTY_RULES}
Return every experience entry from the candidate's profile (same companies, roles and dates), with bullets rewritten/reordered for this job; older roles can have fewer bullets.

Hiring message: warm, specific and human, not generic. Address the contact by first name if known, else "Hi there". Name the role, give 1-2 concrete achievements from her real experience that match this job, mention she is an Adobe Certified Expert when relevant, and her notice period. No flattery, no emojis, no placeholders like [Company]. Sign off with her first name.`,
    content: `CANDIDATE PROFILE (JSON):
${JSON.stringify(resume, null, 2)}

Notice period: ${applicationAnswers.noticePeriod ?? applicationAnswers.noticePeriodDays ?? "not stated"}

JOB:
Title: ${job.title || "(not detected — read it from the text)"}
Company: ${job.company || "(not detected — read it from the text)"}
Location: ${job.location ?? ""}
Hiring contact: ${contact}
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
