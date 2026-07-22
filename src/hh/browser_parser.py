from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path

from playwright.sync_api import sync_playwright


@dataclass
class VacancyPreview:
    hh_id: str
    title: str
    company: str
    url: str


STATE_DIR = Path(__file__).resolve().parent.parent / ".auth"
STATE_FILE = STATE_DIR / "hh_state.json"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_FILE = OUTPUT_DIR / "all_vacancies.json"
SEEN_FILE = OUTPUT_DIR / "seen_vacancies.txt"


class BrowserParser:
    def __init__(self, headless: bool = True, items_per_page: int = 100) -> None:
        self.state_file = STATE_FILE
        self.output_file = OUTPUT_FILE
        self.headless = headless
        self.items_per_page = items_per_page

    def search_by_resume(self, resume_id: str) -> list[VacancyPreview]:
        if not self.state_file.exists():
            print(f"Auth state not found at {self.state_file.resolve()}", file=sys.stderr)
            print("Run `just auth` first to log in.", file=sys.stderr)
            sys.exit(1)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(storage_state=str(self.state_file))
            page = context.new_page()

            # First pass: get total pages
            base_url = (
                f"https://hh.ru/search/vacancy"
                f"?resume={resume_id}"
                f"&area=1"
                f"&search_field=name&search_field=company_name&search_field=description"
                f"&enable_snippets=true"
                f"&hhtmSource=vacancy_search_list"
                f"&hhtmSourceLabel=vacancy_search_list"
                f"&hhtmFrom=vacancy_search_list"
                f"&hhtmFromLabel=drawer_filter"
                f"&L_save_area=true"
                f"&excluded_text=windows%2C+microsoft"
            )
            page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            total_pages = self._get_total_pages(page)
            print(f"Total pages: {total_pages}", file=sys.stderr)

            all_vacancies: dict[str, VacancyPreview] = {}

            for page_idx in range(total_pages):
                url = f"{base_url}&page={page_idx}"
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)

                cards = page.query_selector_all(
                    '[data-qa^="vacancy-serp__vacancy"], '
                    '[data-qa="vacancy-serp-item"]'
                )

                page_count = 0
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
                        hh_id = m.group(1)
                        if hh_id not in all_vacancies:
                            all_vacancies[hh_id] = VacancyPreview(
                                hh_id=hh_id,
                                title=title,
                                company=company,
                                url=vacancy_url,
                            )
                            page_count += 1
                    except Exception:
                        continue

                print(
                    f"  Page {page_idx + 1}/{total_pages}: "
                    f"{len(cards)} cards, {page_count} new, "
                    f"{len(all_vacancies)} total unique",
                    file=sys.stderr,
                )

            browser.close()

        result = list(all_vacancies.values())
        return result

    def _get_total_pages(self, page) -> int:
        pager_pages = page.query_selector_all('[data-qa="pager-page"]')
        last_num = 0
        for pp in pager_pages:
            try:
                n = int(pp.inner_text().strip())
                if n > last_num:
                    last_num = n
            except ValueError:
                continue
        return last_num if last_num > 0 else 1

    def save_to_json(self, vacancies: list[VacancyPreview]) -> None:
        data = [asdict(v) for v in vacancies]
        self.output_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        print(f"Saved {len(vacancies)} vacancies to {self.output_file}", file=sys.stderr)


def load_seen() -> set[str]:
    if not SEEN_FILE.exists():
        return set()
    return {line.strip() for line in SEEN_FILE.read_text().splitlines() if line.strip()}


def main(resume_id: str) -> None:
    parser = BrowserParser()
    t0 = time.time()
    vacancies = parser.search_by_resume(resume_id)
    elapsed = time.time() - t0

    seen_ids = load_seen()
    new_vacancies = [v for v in vacancies if v.hh_id not in seen_ids]

    print(f"\nScraped {len(vacancies)} unique in {elapsed:.0f}s, "
          f"{len(new_vacancies)} new, {len(vacancies) - len(new_vacancies)} already seen",
          file=sys.stderr)
    parser.save_to_json(vacancies)

    if not new_vacancies:
        print("No new vacancies to show.", file=sys.stderr)
        return

    for v in new_vacancies:
        print(f"[{v.hh_id}] {v.title} — {v.company}")
        print(f"    {v.url}")
        print()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("resume_id")
    args = parser.parse_args()
    main(args.resume_id)
