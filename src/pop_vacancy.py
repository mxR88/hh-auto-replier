"""Pop the next unseen vacancy from all_vacancies.json.

- Removes the vacancy from all_vacancies.json (queue pop)
- Adds it to seen_vacancies.txt
- Prints vacancy details
"""

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


def mark_seen(vacancy_id: str) -> None:
    with open(SEEN_FILE, "a") as f:
        f.write(f"{vacancy_id}\n")


def main() -> None:
    seen = load_seen()
    all_vacancies: list[dict] = json.loads(ALL_FILE.read_text())

    # Find first unseen vacancy
    idx = -1
    for i, v in enumerate(all_vacancies):
        if v["hh_id"] not in seen:
            idx = i
            break

    if idx == -1:
        print("❌ Все вакансии просмотрены")
        sys.exit(1)

    v = all_vacancies[idx]

    # Remove from all_vacancies.json
    all_vacancies.pop(idx)
    ALL_FILE.write_text(json.dumps(all_vacancies, ensure_ascii=False))

    # Add to seen
    mark_seen(v["hh_id"])

    print(f"ID: {v['hh_id']}")
    print(f"Должность: {v['title']}")
    print(f"Компания: {v['company']}")
    print(f"URL: {v['url']}")
    print(f"\n(удалена из all_vacancies.json, добавлена в seen_vacancies.txt)")


if __name__ == "__main__":
    main()
