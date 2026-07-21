from __future__ import annotations

import re
from pathlib import Path


def load_resume_skills(path: str) -> set[str]:
    html = Path(path).read_text(encoding="utf-8")
    match = re.search(r'<p class="resume-skils__item">(.*?)</p>', html, re.DOTALL)
    if not match:
        return set()
    raw = match.group(1)
    skills = re.findall(r">([^<]+)<", raw)
    return {s.strip().lower() for s in skills if s.strip()}


def exclude_vacancy(text: str, exclude_words: list[str]) -> bool:
    lower = text.lower()
    return any(w.lower() in lower for w in exclude_words)


def match_vacancy(vacancy_text: str | None, resume_skills: set[str]) -> int:
    if not vacancy_text:
        return 0
    lower = vacancy_text.lower()
    return sum(1 for skill in resume_skills if skill in lower)
