"""Pop the next unseen vacancy from all_vacancies.json and print it."""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ALL_FILE = BASE_DIR / "all_vacancies.json"
SEEN_FILE = BASE_DIR / "seen_vacancies.txt"


def load_seen() -> set[str]:
    if not SEEN_FILE.exists():
        return set()
    return {line.strip() for line in SEEN_FILE.read_text().splitlines() if line.strip()}


def main() -> None:
    seen = load_seen()
    all_vacancies = json.loads(ALL_FILE.read_text())

    for v in all_vacancies:
        if v["hh_id"] not in seen:
            print(f"ID: {v['hh_id']}")
            print(f"Должность: {v['title']}")
            print(f"Компания: {v['company']}")
            print(f"URL: {v['url']}")
            return

    print("❌ Все вакансии просмотрены")
    sys.exit(1)


if __name__ == "__main__":
    main()
