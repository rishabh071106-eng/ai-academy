"""Job discovery.

Two sources:
1. Public ATS job-board APIs (Greenhouse / Lever / Ashby) for companies you
   explicitly watch — reliable JSON, includes full descriptions.
2. Claude server-side web search for broad discovery of senior product roles.
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass, field

import httpx

from .config import Config
from .llm import LLM

UA = {"User-Agent": "job-agent/1.0 (personal job search)"}


@dataclass
class Job:
    url: str
    title: str
    company: str
    source: str
    location: str = ""
    description: str = ""
    extra: dict = field(default_factory=dict)


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", html.unescape(text or "")).strip()


# -- ATS board APIs ---------------------------------------------------------

def fetch_greenhouse(token: str) -> list[Job]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    data = httpx.get(url, headers=UA, timeout=30).raise_for_status().json()
    return [
        Job(
            url=j["absolute_url"],
            title=j.get("title", ""),
            company=token,
            source="greenhouse",
            location=(j.get("location") or {}).get("name", ""),
            description=_strip_html(j.get("content", ""))[:12000],
        )
        for j in data.get("jobs", [])
    ]


def fetch_lever(org: str) -> list[Job]:
    url = f"https://api.lever.co/v0/postings/{org}?mode=json"
    data = httpx.get(url, headers=UA, timeout=30).raise_for_status().json()
    return [
        Job(
            url=j["hostedUrl"],
            title=j.get("text", ""),
            company=org,
            source="lever",
            location=(j.get("categories") or {}).get("location", ""),
            description=(j.get("descriptionPlain") or "")[:12000],
        )
        for j in data
    ]


def fetch_ashby(org: str) -> list[Job]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{org}"
    data = httpx.get(url, headers=UA, timeout=30).raise_for_status().json()
    return [
        Job(
            url=j.get("jobUrl") or j.get("applyUrl", ""),
            title=j.get("title", ""),
            company=org,
            source="ashby",
            location=j.get("location", ""),
            description=_strip_html(j.get("descriptionHtml", ""))[:12000],
        )
        for j in data.get("jobs", [])
        if j.get("isListed", True)
    ]


def discover_from_boards(cfg: Config) -> list[Job]:
    jobs: list[Job] = []
    fetchers = {"greenhouse": fetch_greenhouse, "lever": fetch_lever, "ashby": fetch_ashby}
    for ats, fetch in fetchers.items():
        for org in cfg.companies.get(ats) or []:
            try:
                jobs.extend(fetch(org))
            except Exception as e:  # one bad board must not kill the run
                print(f"  [warn] {ats}/{org} fetch failed: {e}")
    return jobs


# -- Web search discovery ----------------------------------------------------

SEARCH_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["jobs"],
    "properties": {
        "jobs": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["url", "title", "company", "location"],
                "properties": {
                    "url": {"type": "string", "description": "Direct link to the job posting / application page"},
                    "title": {"type": "string"},
                    "company": {"type": "string"},
                    "location": {"type": "string"},
                },
            },
        }
    },
}


def discover_from_web(cfg: Config, llm: LLM) -> list[Job]:
    jobs: list[Job] = []
    blocklist = ", ".join(cfg.blocklist.names)
    for query in cfg.search.get("web_queries", []):
        prompt = (
            "You are sourcing senior product leadership job openings for a candidate "
            "(Director / VP / Head of Product, especially AI-flavored roles, in India "
            "or remote, open to relocation).\n\n"
            f"Run web searches for: {query}\n\n"
            "Find CURRENTLY OPEN postings with a direct application link. Prefer "
            "postings hosted on Greenhouse (boards.greenhouse.io), Lever "
            "(jobs.lever.co), or Ashby (jobs.ashbyhq.com) since those can be applied "
            f"to directly. STRICTLY EXCLUDE any role at, or on behalf of: {blocklist}. "
            "List each posting you found with its exact URL, title, company, and location."
        )
        try:
            findings = llm.ask_with_web_search(prompt, effort="medium")
            extracted = llm.ask_json(
                "Extract every job posting mentioned below into the schema. "
                "Only include entries that have a real, specific posting URL.\n\n"
                + findings,
                SEARCH_SCHEMA,
                effort="low",
                max_tokens=4000,
            )
            for j in extracted["jobs"]:
                if j["url"].startswith("http"):
                    jobs.append(Job(source="web_search", description="", **j))
        except Exception as e:
            print(f"  [warn] web discovery failed for query '{query[:50]}...': {e}")
    return jobs


def fetch_description(job: Job) -> None:
    """Best-effort fetch of a description for web-discovered jobs."""
    if job.description:
        return
    try:
        resp = httpx.get(job.url, headers=UA, timeout=30, follow_redirects=True)
        job.description = _strip_html(resp.text)[:12000]
    except Exception:
        job.description = ""


def discover(cfg: Config, llm: LLM) -> list[Job]:
    jobs = discover_from_boards(cfg) + discover_from_web(cfg, llm)
    # de-dupe by URL within the run
    seen: set[str] = set()
    unique = []
    for j in jobs:
        key = j.url.split("?")[0].rstrip("/").lower()
        if key not in seen:
            seen.add(key)
            unique.append(j)
    return unique
