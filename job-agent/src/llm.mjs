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
    tagline: str,
    summary: str,
    skillGroups: { type: "array", description: "Her skill groups with the same items, reordered so the most relevant come first", items: obj({ name: str, items: strArr }) },
    skills: { ...strArr, description: "Flat list, most relevant first" },
    experience: {
      type: "array",
      items: obj({ company: str, role: str, location: str, client: str, start: str, end: str, bullets: strArr }),
    },
  }),
  hiringMessage: obj({
    subject: { type: "string", description: "Short subject line for an InMail/email" },
    short: { type: "string", description: "Connection-request note, at most 280 characters" },
    full: { type: "string", description: "Message to the hiring manager/recruiter, 60-110 words, use \\n between paragraphs" },
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
Tailored resume: it must stay VERY close to her own resume, so a recruiter who has seen both sees the same document, sharpened for this job:
- Keep her headline unless the role is clearly front-end or full-stack JS, in which case lead with that (e.g. "Senior Full Stack Engineer · Next.js / React + Adobe Commerce"). Keep her tagline, reordering items if useful.
- Summary: keep her summary; you may adjust the first sentence and reorder clauses to match the job. Same length (±15%).
- Experience: every role, same company/role/client/dates. Keep her bullet wording; reorder bullets so the most relevant come first and change at most a few words per bullet to mirror the job's terms where truthful. Keep bold lead-ins like "Peelworks (…):". Don't drop roles or bullets from the two most recent roles.
- Skill groups: same groups and items as hers, reordered by relevance.

Hiring message — write it the way she would actually type it to a stranger on LinkedIn. It must read as genuine and human, not AI-written:
- Open with "Hi <first name>," (or "Hi," if no contact name). Then get straight to the point; no pleasantries like "I hope this message finds you well".
- Say she applied (or is applying) for the exact role, and pick ONE specific thing from this job description that matches her real work, and say it concretely (e.g. "you mention a headless Next.js storefront on Adobe Commerce, which is exactly what I'm building at Altimetrik for Blackhawk Network").
- Add one more relevant proof point with a real project/client name from her experience. Mention Adobe Certified Expert only if the role is Magento/Adobe Commerce.
- Close with a low-pressure ask (a quick chat, or whether they'd be the right person to speak to) and her notice period in passing.
- Plain, warm, confident Indian-English professional tone. Short sentences, 2-3 short paragraphs, 60-110 words. Contractions are fine.
- Banned: "I hope this finds you well", "I am excited/thrilled/delighted", "passionate", "leverage", "synergy", "esteemed", "dynamic", "I came across", "I am writing to", "perfect fit", "add value", "Looking forward to hearing from you", em dashes, emojis, exclamation marks, buzzword lists, flattering the company, placeholders.
- Sign off with just "Aishwarya" (her first name) on its own line.
- subject: 4-8 words, natural, e.g. "Senior Magento role – Adobe Commerce + Next.js". short: a connection note under 280 characters in the same voice.`,
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
- Motivation / free-text questions ("Why do you want to join us?", "Tell us about a project", "Anything else?"): write 2-4 genuine, specific sentences in her voice using her real experience and this job. No clichés, no exclamation marks.
- Voluntary self-identification (race/ethnicity, veteran status, disability, sexual orientation): use the data if present (gender and disability are given); otherwise pick the "decline / prefer not to say / I don't wish to answer" option. Veteran status: she is not a veteran.
- Work authorization outside India / visa sponsorship: she is authorized only in India; for other countries answer that she would need sponsorship.
- If a needed fact is missing or starts with "TODO", or the question asks for something you cannot know (reference names, ID/passport numbers, exact salary history line items), answer exactly __ASK__.
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
  name: str, headline: str,
  tagline: { type: "string", description: "The line of key tech under the headline, e.g. 'Next.js · React · …'" },
  email: str, phone: { type: "string", description: "Digits only, without country code" }, city: str, address: str, linkedinUrl: str,
  totalExperienceYears: { type: "integer" },
  summary: str,
  highlights: { type: "array", description: "'At a glance' stat tiles, if any", items: obj({ value: str, label: str }) },
  skillGroups: { type: "array", description: "Technical skills exactly as grouped on the resume", items: obj({ name: str, items: strArr }) },
  skills: { ...strArr, description: "All skills, flat" },
  experience: {
    type: "array",
    items: obj({ company: str, role: str, location: str, client: { type: "string", description: "e.g. 'Blackhawk Network' or empty" }, start: str, end: str, bullets: strArr }),
  },
  projects: { type: "array", description: "Project index table rows, if any", items: obj({ client: str, platform: str, employer: str, work: str }) },
  education: { type: "array", items: obj({ degree: str, institution: str, status: { type: "string", description: "e.g. 'pursuing' or empty" }, start: str, end: str }) },
  certifications: { type: "array", items: obj({ name: str, issuer: str, date: str }) },
});

/** Turn a resume PDF into a profile.json skeleton. */
export async function extractProfile(pdfBase64) {
  return jsonCall({
    effort: "low",
    schema: PROFILE_SCHEMA,
    system: "Extract the resume into the JSON schema exactly as written: same wording, same bullet text, same skill groups and order. Keep a bullet's bold lead-in like 'Peelworks (Magento 2 Commerce, mobile + web): …' as part of the bullet text. Do not embellish or summarise. Use YYYY-MM for dates and 'present' for current roles. Use empty strings/arrays for missing parts.",
    content: [
      { type: "document", source: { type: "base64", media_type: "application/pdf", data: pdfBase64 } },
      { type: "text", text: "Extract this resume." },
    ],
  });
}
