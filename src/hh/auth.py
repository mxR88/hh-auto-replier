from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

STATE_DIR = Path(__file__).resolve().parent.parent / ".auth"
STATE_FILE = STATE_DIR / "hh_state.json"


def login() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://hh.ru", wait_until="networkidle")

        print("Browser opened. Please log in to hh.ru in the browser window.")
        print("After logging in, press Enter in this terminal to save the session and close the browser.")
        input()

        context.storage_state(path=str(STATE_FILE))
        print(f"Session saved to {STATE_FILE.resolve()}")
        browser.close()


if __name__ == "__main__":
    login()
