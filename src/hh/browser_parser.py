from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import IO

from playwright.sync_api import sync_playwright


@dataclass
class VacancyPreview:
    hh_id: str
    title: str
    company: str
    url: str


STATE_DIR = Path(__file__).resolve().parent.parent / ".auth"
STATE_FILE = STATE_DIR / "hh_state.json"


class BrowserParser:
    def __init__(self) -> None:
        self.state_file = STATE_FILE

    def search_by_resume(self, resume_id: str) -> list[VacancyPreview]:
        if not self.state_file.exists():
            print(f"Auth state not found at {self.state_file.resolve()}", file=sys.stderr)
            print("Run `just auth` first to log in.", file=sys.stderr)
            sys.exit(1)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=str(self.state_file))
            page = context.new_page()
            url = f"https://hh.ru/search/vacancy?resume={resume_id}"
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(3000)

            vacancies = self._parse_vacancies(page)

            # Try next pages
            page_num = 0
            while True:
                next_btn = page.query_selector('[data-qa="pager-next"]')
                if not next_btn:
                    break
                page_num += 1
                next_btn.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(2000)
                vacancies.extend(self._parse_vacancies(page))

            browser.close()

        return vacancies

    def _parse_vacancies(self, page) -> list[VacancyPreview]:
        result: list[VacancyPreview] = []
        cards = page.query_selector_all('[data-qa^="vacancy-serp__vacancy"]')
        if not cards:
            cards = page.query_selector_all('[data-qa="vacancy-serp-item"]')

        for card in cards:
            try:
                link_el = card.query_selector('[data-qa="serp-item__title"]')
                if not link_el:
                    continue
                href = link_el.get_attribute("href") or ""
                title = link_el.inner_text().strip()
                m = re.search(r"/vacancy/(\d+)", href)
                if not m:
                    continue
                company_el = card.query_selector(
                    '[data-qa="vacancy-serp__vacancy-employer"], '
                    '[data-qa="vacancy-serp__vacancy-employer-name"]'
                )
                company = company_el.inner_text().strip() if company_el else ""
                vacancy_url = href if href.startswith("http") else f"https://hh.ru{href}"
                result.append(VacancyPreview(
                    hh_id=m.group(1),
                    title=title,
                    company=company,
                    url=vacancy_url,
                ))
            except Exception:
                continue

        return result


def main(resume_id: str) -> None:
    parser = BrowserParser()
    vacancies = parser.search_by_resume(resume_id)
    for v in vacancies:
        print(f"[{v.hh_id}] {v.title} — {v.company}")
        print(f"    {v.url}")
        print()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("resume_id")
    args = parser.parse_args()
    main(args.resume_id)
