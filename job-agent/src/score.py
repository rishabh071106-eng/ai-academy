"""Fit scoring: should the agent spend an application on this job?"""

from __future__ import annotations

from .config import Config
from .discover import Job
from .llm import LLM

SCORE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["fit_score", "decision", "blocked", "seniority_ok", "emphasis", "reasons"],
    "properties": {
        "fit_score": {"type": "integer", "description": "0-100 overall fit"},
        "decision": {"type": "string", "enum": ["apply", "skip"]},
        "blocked": {
            "type": "boolean",
            "description": "True if the employer or end-client is a blocklisted company",
        },
        "seniority_ok": {
            "type": "boolean",
            "description": "True only for Director / VP / Head-of level (or higher) roles",
        },
        "emphasis": {
            "type": "string",
            "enum": ["ai_leadership", "product_leadership", "fintech_domain"],
            "description": "Which resume emphasis fits this job best",
        },
        "reasons": {"type": "string", "description": "2-4 sentence justification"},
    },
}


def score_job(job: Job, cfg: Config, llm: LLM) -> dict:
    blocklist = ", ".join(cfg.blocklist.names)
    prompt = f"""You are screening a job for a candidate. Decide whether it is worth applying.

CANDIDATE (summary):
{cfg.resume_master[:4000]}

CANDIDATE TARGETS: Director / VP / Head of Product roles (especially AI product
leadership), in India or remote, open to relocation. Currently a VP at JP Morgan,
so the role should be a lateral senior move or step up — NOT an IC PM or manager-level role.

HARD RULES:
- blocked=true if the employer, parent company, or end-client is any of: {blocklist}.
  This includes staffing agencies or consultancies hiring FOR these companies.
- seniority_ok=false for roles below Director level (Senior PM, Group PM, Lead PM = skip).

JOB:
Company: {job.company}
Title: {job.title}
Location: {job.location}
URL: {job.url}
Description:
{job.description[:8000] or "(no description available — judge from title/company, be conservative)"}

Score holistically: seniority match, domain fit (AI / fintech / platform), location
feasibility, and how compelling this candidate would be to the hiring team."""

    result = llm.ask_json(prompt, SCORE_SCHEMA, effort="medium", max_tokens=2000)

    # Belt and braces: re-check blocklist mechanically regardless of model output.
    if cfg.blocklist.matches(job.company):
        result["blocked"] = True
    if result["blocked"] or not result["seniority_ok"]:
        result["decision"] = "skip"
    return result
