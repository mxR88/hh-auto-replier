from __future__ import annotations

import re
import sys
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from config import Config

SEEN_FILE = Path(__file__).resolve().parent.parent / "seen_vacancies.txt"


def mark_seen(vacancy_id: str) -> None:
    with open(SEEN_FILE, "a") as f:
        f.write(f"{vacancy_id}\n")


def extract_vacancy_id(url: str) -> str:
    m = re.search(r"vacancy/(\d+)", url)
    if not m:
        print("❌ Could not extract vacancy ID from URL")
        sys.exit(1)
    return m.group(1)


def strip_html(html: str) -> str:
    return BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)


def get_vacancy_details(cfg: Config, vacancy_id: str) -> dict:
    headers = {
        "User-Agent": cfg.hh_user_agent,
        "Authorization": f"Bearer {cfg.app_token}",
    }
    resp = httpx.get(f"{cfg.hh_api_base}/vacancies/{vacancy_id}", headers=headers)
    resp.raise_for_status()
    return resp.json()


def print_vacancy_info(vacancy: dict) -> None:
    name = vacancy.get("name", "—")
    employer = (vacancy.get("employer") or {}).get("name", "—")
    snippet = vacancy.get("snippet") or {}
    requirement = snippet.get("requirement", "") or ""
    responsibility = snippet.get("responsibility", "") or ""
    description = vacancy.get("description", "") or ""
    key_skills = [s["name"] for s in (vacancy.get("key_skills") or [])]

    print(f"Название: {name}")
    print(f"Компания: {employer}")
    print()
    if description:
        print("Описание:")
        print(strip_html(description))
        print()
    if requirement:
        print("Требования:")
        print(strip_html(requirement))
        print()
    if responsibility:
        print("Обязанности:")
        print(strip_html(responsibility))
        print()
    if key_skills:
        print("Ключевые навыки:", ", ".join(key_skills))
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python src/vacancy_info.py <vacancy_url>")
        sys.exit(1)

    url = sys.argv[1]
    m = re.search(r"vacancy/(\d+)", url)
    if not m:
        print("❌ Could not extract vacancy ID from URL")
        sys.exit(1)
    vacancy_id = m.group(1)

    cfg = Config()
    headers = {
        "User-Agent": cfg.hh_user_agent,
        "Authorization": f"Bearer {cfg.app_token}",
    }
    resp = httpx.get(f"{cfg.hh_api_base}/vacancies/{vacancy_id}", headers=headers)
    resp.raise_for_status()
    d = resp.json()

    print_vacancy_info(d)
    mark_seen(vacancy_id)
    print(f"(ID {vacancy_id} добавлен в seen_vacancies.txt)")