from pathlib import Path

from config import Config
from hh.client import HHClient
from hh.matcher import exclude_vacancy, load_resume_skills, match_vacancy
from hh.models import Vacancy

SEEN_FILE = Path(__file__).resolve().parent.parent / "seen_vacancies.txt"


def load_seen() -> set[int]:
    if not SEEN_FILE.exists():
        return set()
    return {int(line.strip()) for line in SEEN_FILE.read_text().splitlines() if line.strip()}


def mark_seen(vacancy_id: int) -> None:
    with open(SEEN_FILE, "a") as f:
        f.write(f"{vacancy_id}\n")


def run() -> None:
    cfg = Config()
    client = HHClient(cfg)

    print(f"Loading resume skills...")
    resume_skills = load_resume_skills(cfg.resume_path)
    print(f"Found {len(resume_skills)} skills in resume")
    print()

    print(f"Search params:")
    print(f"  text:       {cfg.search_text}")
    print(f"  area:       {cfg.search_area}")
    print(f"  schedule:   {cfg.search_schedule}")
    print(f"  salary_from:{cfg.salary_from}")
    print(f"  per_page:   {cfg.search_per_page}")
    print(f"  pages:      5")
    print(f"  exclude:    {cfg.exclude_words}")
    print()

    seen = load_seen()
    print(f"Already seen: {len(seen)} vacancies")
    print()

    exclude = cfg.exclude_words
    allowed_areas = set(cfg.search_area)
    matched: list[tuple[int, Vacancy]] = []

    for page in range(5):
        data = client.search_vacancies(page=page)
        items = data.get("items", [])
        if not items:
            break
        for raw in items:
            v = Vacancy.from_api(raw)
            if v.id in seen:
                continue
            area_id = (raw.get("area") or {}).get("id")
            if area_id is not None:
                try:
                    if int(area_id) not in allowed_areas:
                        continue
                except ValueError:
                    pass
            combined = " ".join(filter(None, [v.name, v.requirement_raw, v.responsibility_raw, *v.key_skills]))
            if exclude_vacancy(combined, exclude):
                continue
            score = match_vacancy(combined, resume_skills)
            matched.append((score, v))

    matched.sort(key=lambda x: x[0], reverse=True)

    print(f"\n{'='*70}")
    print(f"Matched {len(matched)} relevant vacancies (sorted by relevance):")
    print(f"{'='*70}\n")

    for score, v in matched[:20]:
        print(f"[{score:2d}] {v.name}")
        print(f"     {v.employer_name} | {v.area} | {v.schedule}")
        sal = f"{v.salary_from or '?'}-{v.salary_to or '?'} {v.salary_currency or ''}"
        print(f"     {sal} | {v.experience} | {v.employment}")
        print(f"     {v.alternate_url}")
        print()


if __name__ == "__main__":
    run()