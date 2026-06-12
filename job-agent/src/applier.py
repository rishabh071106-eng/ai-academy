"""Application submission via browser automation (Playwright).

Strategy: instead of hardcoding per-ATS selectors (which rot), we scrape the
form's visible fields, ask Claude to map each field to an answer from the
candidate's profile, fill, and submit.

Safety rails:
- A required field Claude cannot answer from the profile => route to review
  queue, never guess.
- CAPTCHA / login wall detected => route to review queue.
- auto_submit=false in config => fill everything, screenshot, save for review.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

from .config import Config
from .discover import Job
from .llm import LLM

ANSWER_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["answers", "can_complete", "reason"],
    "properties": {
        "can_complete": {
            "type": "boolean",
            "description": "False if any REQUIRED field cannot be answered truthfully from the profile",
        },
        "reason": {"type": "string"},
        "answers": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["field_id", "kind", "value"],
                "properties": {
                    "field_id": {"type": "string", "description": "The data-ja-id of the field"},
                    "kind": {"type": "string", "enum": ["text", "select", "checkbox", "skip"]},
                    "value": {"type": "string", "description": "Text to type, exact option label to select, 'true'/'false' for checkbox, or '' for skip"},
                },
            },
        },
    },
}


@dataclass
class ApplyResult:
    status: str  # applied | review | failed
    detail: str


def _collect_fields(page: Page) -> list[dict]:
    """Tag every visible form control with data-ja-id and describe it."""
    return page.evaluate(
        """() => {
        const fields = [];
        let i = 0;
        for (const el of document.querySelectorAll('input, textarea, select')) {
            if (el.type === 'hidden' || el.offsetParent === null) continue;
            const id = 'ja-' + (i++);
            el.setAttribute('data-ja-id', id);
            let label = '';
            if (el.labels && el.labels.length) label = el.labels[0].innerText;
            else if (el.getAttribute('aria-label')) label = el.getAttribute('aria-label');
            else if (el.placeholder) label = el.placeholder;
            const options = el.tagName === 'SELECT'
                ? [...el.options].map(o => o.label).slice(0, 50) : null;
            fields.push({
                field_id: id,
                tag: el.tagName.toLowerCase(),
                type: el.type || '',
                name: el.name || '',
                label: (label || '').trim().slice(0, 300),
                required: el.required || el.getAttribute('aria-required') === 'true',
                options: options,
            });
        }
        return fields;
    }"""
    )


def _has_captcha(page: Page) -> bool:
    return page.evaluate(
        """() => !!document.querySelector(
            'iframe[src*="recaptcha"], iframe[src*="hcaptcha"], iframe[src*="turnstile"], .g-recaptcha, .h-captcha'
        )"""
    )


def _plan_answers(fields: list[dict], job: Job, cfg: Config, cover_letter: str, llm: LLM) -> dict:
    prompt = f"""You are filling a job application form on behalf of this candidate.

CANDIDATE PROFILE (authoritative — answer ONLY from this):
{json.dumps(cfg.profile, indent=2, default=str)}

COVER LETTER (use for any cover-letter textarea):
{cover_letter}

JOB: {job.title} at {job.company} ({job.url})

FORM FIELDS:
{json.dumps(fields, indent=2)}

Rules:
- File-upload fields are handled separately; mark them kind=skip.
- For selects, value must be one of the listed option labels, copied exactly.
- Demographic/EEO questions: prefer "Decline to self identify" style options if present.
- Never invent facts. If a REQUIRED field needs information not in the profile
  (e.g. salary number when none is given, references, ID numbers), set
  can_complete=false and explain in reason.
- Optional fields you can't answer: kind=skip."""

    return llm.ask_json(prompt, ANSWER_SCHEMA, effort="medium", max_tokens=8000)


def _fill(page: Page, answers: list[dict], resume_path: Path) -> None:
    # Resume upload first — every visible file input gets the resume.
    for file_input in page.query_selector_all('input[type="file"]'):
        try:
            file_input.set_input_files(str(resume_path))
        except Exception:
            pass

    for ans in answers:
        if ans["kind"] == "skip":
            continue
        el = page.query_selector(f'[data-ja-id="{ans["field_id"]}"]')
        if el is None:
            continue
        try:
            if ans["kind"] == "text":
                el.fill(ans["value"])
            elif ans["kind"] == "select":
                el.select_option(label=ans["value"])
            elif ans["kind"] == "checkbox":
                el.set_checked(ans["value"].lower() == "true")
        except Exception as e:
            print(f"  [warn] could not fill {ans['field_id']} ({ans['value'][:40]}): {e}")


def apply_to_job(job: Job, pkg_dir: Path, cfg: Config, llm: LLM) -> ApplyResult:
    cover_letter = (pkg_dir / "cover_letter.txt").read_text()
    resume_path = pkg_dir / "resume.docx"
    auto_submit = bool(cfg.policy.get("auto_submit", False))

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(job.url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)

            # Greenhouse/Lever often have an "Apply" button leading to the form.
            for label in ("Apply for this job", "Apply Now", "Apply now", "Apply"):
                btn = page.get_by_role("button", name=label).first
                link = page.get_by_role("link", name=label).first
                try:
                    if btn.is_visible():
                        btn.click()
                        break
                    if link.is_visible():
                        link.click()
                        break
                except Exception:
                    continue
            page.wait_for_timeout(2000)

            if _has_captcha(page):
                page.screenshot(path=str(pkg_dir / "page.png"), full_page=True)
                return ApplyResult("review", "CAPTCHA detected — complete manually from review packet")

            fields = _collect_fields(page)
            if not fields:
                page.screenshot(path=str(pkg_dir / "page.png"), full_page=True)
                return ApplyResult("review", "No fillable form found (login wall or unsupported ATS)")

            plan = _plan_answers(fields, job, cfg, cover_letter, llm)
            (pkg_dir / "form_plan.json").write_text(json.dumps(plan, indent=2))
            if not plan["can_complete"]:
                page.screenshot(path=str(pkg_dir / "page.png"), full_page=True)
                return ApplyResult("review", f"Needs your input: {plan['reason']}")

            _fill(page, plan["answers"], resume_path)
            page.screenshot(path=str(pkg_dir / "filled.png"), full_page=True)

            if not auto_submit:
                return ApplyResult("review", "auto_submit=false — form filled and screenshotted for review")

            submit = page.query_selector(
                'button[type="submit"], input[type="submit"], button:has-text("Submit")'
            )
            if submit is None:
                return ApplyResult("review", "Submit button not found — review packet saved")
            submit.click()
            page.wait_for_timeout(5000)

            if _has_captcha(page):
                page.screenshot(path=str(pkg_dir / "page.png"), full_page=True)
                return ApplyResult("review", "CAPTCHA appeared at submit — complete manually")

            page.screenshot(path=str(pkg_dir / "confirmation.png"), full_page=True)
            return ApplyResult("applied", "Submitted; confirmation screenshot saved")
        except Exception as e:
            try:
                page.screenshot(path=str(pkg_dir / "error.png"), full_page=True)
            except Exception:
                pass
            return ApplyResult("failed", f"{type(e).__name__}: {e}")
        finally:
            browser.close()
