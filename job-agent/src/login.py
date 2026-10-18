"""One-time interactive login: python -m src.login naukri|linkedin

Opens a real browser window. Log in normally (OTP/2FA fine). The session is
saved locally and reused by the agent — your password is never stored.
"""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

from .sessions import LOGIN_URLS, is_logged_in, launch_persistent


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in LOGIN_URLS:
        print(f"usage: python -m src.login [{'|'.join(LOGIN_URLS)}]")
        sys.exit(1)
    site = sys.argv[1]
    with sync_playwright() as pw:
        ctx = launch_persistent(pw, site, headless=False)
        page = ctx.new_page()
        page.goto(LOGIN_URLS[site])
        input(f"\nLog in to {site} in the browser window (OTP/2FA is fine).\n"
              "Press Enter here when you're done... ")
        page.close()
        if is_logged_in(ctx, site):
            print(f"{site}: session saved. The agent can now use it headlessly.")
        else:
            print(f"{site}: could not confirm login — try again.")
        ctx.close()


if __name__ == "__main__":
    main()
