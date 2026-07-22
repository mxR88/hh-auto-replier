"""Mark a vacancy as seen (skip it). Accepts URL or numeric ID."""

import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SEEN_FILE = BASE_DIR / "seen_vacancies.txt"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run python src/skip_vacancy.py <vacancy_id_or_url>")
        sys.exit(1)

    arg = sys.argv[1]
    m = re.search(r"vacancy/(\d+)", arg)
    if m:
        vacancy_id = m.group(1)
    elif arg.isdigit():
        vacancy_id = arg
    else:
        print(f"❌ Can't parse vacancy ID from: {arg}")
        sys.exit(1)

    with open(SEEN_FILE, "a") as f:
        f.write(f"{vacancy_id}\n")
    print(f"✓ Вакансия {vacancy_id} пропущена (добавлена в seen_vacancies.txt)")


if __name__ == "__main__":
    main()
