"""LinkedIn discovery and (optional) Easy Apply (uses your saved login session).

⚠️ Risk disclosure: LinkedIn actively detects automation and can restrict or
ban accounts. For a senior candidate, the LinkedIn profile itself is a career
asset, so the defaults here are deliberately conservative:

- Discovery (browsing job search results at human pace, low volume): on.
- Jobs with an EXTERNAL apply link: handed to the generic form-filler —
  the application happens off-LinkedIn, so there's no platform risk.
- Easy Apply: config `linkedin.easy_apply: review` (default) fills nothing on
  LinkedIn; it saves a packet so you submit in one click. Set it to `auto` only
  if you accept the account-restriction risk — the agent then completes the
  Easy Apply modal, capped and rate-limited.
"""

from __future__ import annotations

import random
import re
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import Page, sync_playwright

from .applier import ApplyResult, _collect_fields, _fill, _plan_answers
from .config import Config
from .discover import Job
from .llm import LLM
from .sessions import is_logged_in, launch_persistent


def _pause(page: Page, lo: int = 2000, hi: int = 5000) -> None:
    page.wait_for_timeout(random.randint(lo, hi))


def discover(cfg: Config) -> list[Job]:
    li = cfg.raw.get("linkedin", {}) or {}
    if not li.get("enabled"):
        return []
    jobs: list[Job] = []
    max_per_query = int(li.get("max_results_per_query", 15))
    with sync_playwright() as pw:
        ctx = launch_persistent(pw, "linkedin")
        try:
            if not is_logged_in(ctx, "linkedin"):
                print("  [warn] linkedin: not logged in — run: python -m src.login linkedin")
                return []
            page = ctx.new_page()
            for kw in li.get("keywords", []):
                url = (f"https://www.linkedin.com/jobs/search/?keywords={quote(kw)}"
                       f"&location={quote(li.get('location', 'India'))}&f_TPR=r604800")
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    _pause(page, 4000, 7000)
                    cards = page.eval_on_selector_all(
                        'a[href*="/jobs/view/"]',
                        "els => els.map(e => ({url: e.href, title: e.innerText.trim()}))",
                    )
                    seen = set()
                    for c in cards:
                        m = re.search(r"/jobs/view/(\d+)", c["url"])
                        if not m or m.group(1) in seen or not c["title"]:
                            continue
                        seen.add(m.group(1))
                        jobs.append(Job(
                            url=f"https://www.linkedin.com/jobs/view/{m.group(1)}/",
                            title=c["title"].splitlines()[0][:200],
                            company="",
                            source="linkedin",
                        ))
                        if len(seen) >= max_per_query:
                            break
                except Exception as e:
                    print(f"  [warn] linkedin search failed ({kw}): {e}")
        finally:
            ctx.close()
    print(f"  linkedin: {len(jobs)} postings")
    return jobs


def enrich(job: Job) -> None:
    with sync_playwright() as pw:
        ctx = launch_persistent(pw, "linkedin")
        try:
            page = ctx.new_page()
            page.goto(job.url, wait_until="domcontentloaded", timeout=60000)
            _pause(page, 3000, 5000)
            for sel in ('[class*="company-name"]', ".topcard__org-name-link",
                        'a[href*="/company/"]'):
                el = page.query_selector(sel)
                if el and el.inner_text().strip():
                    job.company = el.inner_text().strip().splitlines()[0][:120]
                    break
            body = page.evaluate("() => document.body.innerText")
            job.description = body[:12000]
            job.extra["easy_apply"] = page.query_selector(
                'button:has-text("Easy Apply")') is not None
        except Exception as e:
            print(f"  [warn] linkedin enrich failed: {e}")
        finally:
            ctx.close()


def _easy_apply_auto(page: Page, job: Job, pkg_dir: Path, cfg: Config,
                     llm: LLM, cover_letter: str) -> ApplyResult:
    resume = pkg_dir / "resume.docx"
    for step in range(10):  # Easy Apply modals are multi-page
        _pause(page, 1500, 3000)
        fields = _collect_fields(page)
        if fields:
            plan = _plan_answers(fields, job, cfg, cover_letter, llm)
            if not plan["can_complete"]:
                page.screenshot(path=str(pkg_dir / "easy_apply.png"))
                return ApplyResult("review", f"Easy Apply needs your input: {plan['reason']}")
            _fill(page, plan["answers"], resume)
        _pause(page, 800, 1500)

        submit = page.query_selector('button[aria-label*="Submit application"]')
        if submit:
            submit.click()
            _pause(page, 3000, 5000)
            page.screenshot(path=str(pkg_dir / "confirmation.png"))
            return ApplyResult("applied", "Easy Apply submitted")
        nxt = page.query_selector(
            'button[aria-label*="Continue to next"], button[aria-label*="Review your application"]')
        if nxt is None:
            break
        nxt.click()
    page.screenshot(path=str(pkg_dir / "easy_apply.png"))
    return ApplyResult("review", "Easy Apply flow didn't reach submit — finish manually")


def apply_to_job(job: Job, pkg_dir: Path, cfg: Config, llm: LLM) -> ApplyResult:
    li = cfg.raw.get("linkedin", {}) or {}
    mode = li.get("easy_apply", "review")
    cover_letter_path = pkg_dir / "cover_letter.txt"
    cover_letter = cover_letter_path.read_text() if cover_letter_path.exists() else ""

    with sync_playwright() as pw:
        ctx = launch_persistent(pw, "linkedin")
        page = ctx.new_page()
        try:
            page.goto(job.url, wait_until="domcontentloaded", timeout=60000)
            _pause(page, 3000, 5000)

            easy = page.query_selector('button:has-text("Easy Apply")')
            if easy is None:
                # External apply: grab the off-LinkedIn URL and let the generic
                # form-filler handle it (no platform risk).
                apply_btn = page.query_selector('button:has-text("Apply"), a:has-text("Apply")')
                if apply_btn is None:
                    page.screenshot(path=str(pkg_dir / "page.png"))
                    return ApplyResult("review", "No apply button found on LinkedIn page")
                with ctx.expect_page(timeout=15000) as new_page_info:
                    apply_btn.click()
                external_url = new_page_info.value.url
                from .applier import apply_to_job as generic_apply
                external_job = Job(url=external_url, title=job.title,
                                   company=job.company, source="linkedin-external",
                                   description=job.description)
                return generic_apply(external_job, pkg_dir, cfg, llm)

            if mode != "auto":
                page.screenshot(path=str(pkg_dir / "easy_apply.png"))
                return ApplyResult(
                    "review",
                    "Easy Apply queued for your one-click submit "
                    "(set linkedin.easy_apply: auto to automate — account-restriction risk)",
                )
            easy.click()
            return _easy_apply_auto(page, job, pkg_dir, cfg, llm, cover_letter)
        except Exception as e:
            try:
                page.screenshot(path=str(pkg_dir / "error.png"))
            except Exception:
                pass
            return ApplyResult("failed", f"{type(e).__name__}: {e}")
        finally:
            ctx.close()
