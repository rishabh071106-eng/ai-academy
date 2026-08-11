"""Persistent, password-free browser sessions for job portals.

You log in ONCE interactively (python -m src.login <site>) — including any
OTP/2FA — and the session is persisted to state/browser/<site>/ (git-ignored).
The agent then reuses it headless. No credentials are ever stored in code,
config, or the repo.
"""

from __future__ import annotations

from playwright.sync_api import BrowserContext, Playwright

from .config import ROOT

BROWSER_STATE = ROOT / "state" / "browser"

LOGIN_URLS = {
    "naukri": "https://www.naukri.com/nlogin/login",
    "linkedin": "https://www.linkedin.com/login",
}

# Selector that only renders for a logged-in user.
LOGGED_IN_MARKERS = {
    "naukri": ('https://www.naukri.com/mnjuser/homepage', '[class*="nI-gNb-drawer"], [class*="user-name"], img[alt*="profile" i]'),
    "linkedin": ("https://www.linkedin.com/feed/", "#global-nav, .global-nav__me"),
}


def launch_persistent(pw: Playwright, site: str, headless: bool = True) -> BrowserContext:
    profile_dir = BROWSER_STATE / site
    profile_dir.mkdir(parents=True, exist_ok=True)
    return pw.chromium.launch_persistent_context(
        str(profile_dir),
        headless=headless,
        viewport={"width": 1366, "height": 900},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        ),
    )


def is_logged_in(ctx: BrowserContext, site: str) -> bool:
    url, marker = LOGGED_IN_MARKERS[site]
    page = ctx.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)
        if site == "linkedin" and "/login" in page.url:
            return False
        return page.query_selector(marker) is not None
    except Exception:
        return False
    finally:
        page.close()
