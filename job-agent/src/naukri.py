"""Naukri.com discovery and auto-apply (uses your saved login session).

Notes on how Naukri applies work:
- One-click "Apply" uses the resume stored on YOUR NAUKRI PROFILE — per-job
  resume swaps aren't possible, so keep that profile resume strong and current.
- Some jobs pop a chatbot questionnaire; the agent answers from
  profile/profile.yaml via Claude and never invents facts (otherwise -> review).
- "Apply on company site" jobs are routed to the generic form-filler.

Portal DOMs change. Every step is wrapped so an unexpected page degrades to a
review packet with a screenshot — never a wrong or half-submitted application.
"""

from __future__ import annotations

import random
import re
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

from .applier import ApplyResult
from .config import Config
from .discover import Job
from .llm import LLM
from .sessions import is_logged_in, launch_persistent

ANSWER_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["answer", "can_answer"],
    "properties": {
        "can_answer": {
            "type": "boolean",
            "description": "False if the question cannot be answered truthfully from the profile",
        },
        "answer": {
            "type": "string",
            "description": "Short answer text, or the exact option label to pick",
        },
    },
}


def _pause(page: Page, lo: int = 1500, hi: int = 3500) -> None:
    page.wait_for_timeout(random.randint(lo, hi))


def discover(cfg: Config) -> list[Job]:
    n = cfg.raw.get("naukri", {}) or {}
    if not n.get("enabled"):
        return []
    jobs: list[Job] = []
    with sync_playwright() as pw:
        ctx = launch_persistent(pw, "naukri")
        try:
            if not is_logged_in(ctx, "naukri"):
                print("  [warn] naukri: not logged in — run: python -m src.login naukri")
                return []
            page = ctx.new_page()
            for kw in n.get("keywords", []):
                for loc in n.get("locations", ["india"]):
                    slug = re.sub(r"\s+", "-", kw.strip().lower())
                    loc_slug = re.sub(r"\s+", "-", loc.strip().lower())
                    url = f"https://www.naukri.com/{slug}-jobs-in-{loc_slug}"
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=60000)
                        _pause(page, 3000, 5000)
                        cards = page.eval_on_selector_all(
                            'a[href*="job-listings"]',
                            "els => els.map(e => ({url: e.href, title: e.innerText.trim()}))",
                        )
                        for c in cards:
                            if c["title"] and len(c["title"]) > 5:
                                jobs.append(Job(
                                    url=c["url"].split("?")[0],
                                    title=c["title"].splitlines()[0][:200],
                                    company="",
                                    source="naukri",
                                ))
                    except Exception as e:
                        print(f"  [warn] naukri search failed ({kw}/{loc}): {e}")
        finally:
            ctx.close()
    print(f"  naukri: {len(jobs)} postings")
    return jobs


def _extract_company(page: Page) -> str:
    for sel in ('[class*="comp-name"]', '[class*="companyName"]',
                '[class*="jd-header"] a', ".about-company h2"):
        el = page.query_selector(sel)
        if el:
            text = el.inner_text().strip()
            if text:
                return text.splitlines()[0][:120]
    return ""


def enrich(job: Job) -> None:
    """Fill in company + description from the job page (needs session)."""
    with sync_playwright() as pw:
        ctx = launch_persistent(pw, "naukri")
        try:
            page = ctx.new_page()
            page.goto(job.url, wait_until="domcontentloaded", timeout=60000)
            _pause(page, 2500, 4000)
            job.company = _extract_company(page) or job.company
            body = page.evaluate("() => document.body.innerText")
            job.description = body[:12000]
        except Exception as e:
            print(f"  [warn] naukri enrich failed: {e}")
        finally:
            ctx.close()


def _answer_chatbot(page: Page, cfg: Config, llm: LLM, pkg_dir: Path) -> ApplyResult | None:
    """Handle the post-apply questionnaire drawer. Returns a terminal result
    or None if there was no questionnaire / it completed."""
    import json

    drawer_sel = '[class*="chatbot"], [class*="Chatbot"]'
    if not page.query_selector(drawer_sel):
        return None

    asked: list[str] = []
    for _ in range(15):  # max 15 questions
        _pause(page, 1200, 2200)
        drawer = page.query_selector(drawer_sel)
        if drawer is None:
            return None  # drawer closed — done
        bot_msgs = page.query_selector_all('[class*="botMsg"], [class*="bot-msg"]')
        question = bot_msgs[-1].inner_text().strip() if bot_msgs else ""
        if not question or (asked and question == asked[-1] and len(asked) > 2):
            break
        asked.append(question)

        options = [o.inner_text().strip() for o in page.query_selector_all(
            '[class*="chatbot"] label, [class*="radio-btn"] label, [class*="chip"]') if o.inner_text().strip()]

        plan = llm.ask_json(
            "Answer this job-application screening question ONLY from the profile. "
            "If options are listed, 'answer' must be one option copied exactly.\n\n"
            f"PROFILE:\n{json.dumps(cfg.profile, default=str)}\n\n"
            f"QUESTION: {question}\n"
            f"OPTIONS: {options or 'free text'}",
            ANSWER_SCHEMA, effort="low", max_tokens=500,
        )
        if not plan["can_answer"]:
            page.screenshot(path=str(pkg_dir / "chatbot.png"))
            return ApplyResult("review", f"Chatbot question needs your input: {question[:120]}")

        try:
            if options:
                page.get_by_text(plan["answer"], exact=True).first.click()
            else:
                box = page.query_selector(
                    '[class*="chatbot"] input:not([type=hidden]), '
                    '[class*="chatbot"] div[contenteditable="true"], '
                    '[class*="InputBox"] input')
                if box is None:
                    raise RuntimeError("no input box found")
                box.fill(plan["answer"]) if box.get_attribute("contenteditable") != "true" \
                    else box.type(plan["answer"])
            _pause(page, 600, 1200)
            send = page.query_selector('[class*="sendMsg"], [class*="send-msg"], '
                                       '[class*="chatbot"] button[type="submit"]')
            if send:
                send.click()
        except Exception as e:
            page.screenshot(path=str(pkg_dir / "chatbot.png"))
            return ApplyResult("review", f"Chatbot UI changed ({e}); finish manually: {question[:100]}")
    return None


def apply_to_job(job: Job, pkg_dir: Path, cfg: Config, llm: LLM) -> ApplyResult:
    with sync_playwright() as pw:
        ctx = launch_persistent(pw, "naukri")
        page = ctx.new_page()
        try:
            page.goto(job.url, wait_until="domcontentloaded", timeout=60000)
            _pause(page, 2500, 4500)

            if page.query_selector('#already-applied, [class*="already-applied"]'):
                return ApplyResult("applied", "Was already applied on Naukri")

            if page.query_selector("#company-site-button"):
                return ApplyResult("review",
                                   f"Apply happens on company site — open manually or via packet: {job.url}")

            btn = page.query_selector("#apply-button") or \
                page.get_by_role("button", name=re.compile(r"^\s*Apply\s*$", re.I)).first
            if not btn:
                page.screenshot(path=str(pkg_dir / "page.png"))
                return ApplyResult("review", "Apply button not found")
            btn.click()
            _pause(page, 2500, 4000)

            chatbot_result = _answer_chatbot(page, cfg, llm, pkg_dir)
            if chatbot_result:
                return chatbot_result

            _pause(page, 1500, 2500)
            body = page.evaluate("() => document.body.innerText").lower()
            page.screenshot(path=str(pkg_dir / "confirmation.png"))
            if "successfully applied" in body or "application sent" in body \
                    or page.query_selector('#already-applied, [class*="already-applied"]'):
                return ApplyResult("applied", "Applied on Naukri (uses your Naukri profile resume)")
            return ApplyResult("review", "Apply clicked but no confirmation detected — verify from screenshot")
        except Exception as e:
            try:
                page.screenshot(path=str(pkg_dir / "error.png"))
            except Exception:
                pass
            return ApplyResult("failed", f"{type(e).__name__}: {e}")
        finally:
            ctx.close()
