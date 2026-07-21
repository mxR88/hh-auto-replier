from __future__ import annotations

import re
import sys

import httpx

from config import Config
from hh.matcher import load_resume_skills


def extract_vacancy_id(url: str) -> str:
    m = re.search(r"vacancy/(\d+)", url)
    if not m:
        print("❌ Could not extract vacancy ID from URL")
        sys.exit(1)
    return m.group(1)


def get_vacancy_details(cfg: Config, vacancy_id: str) -> dict:
    token = cfg.access_token
    headers = {
        "User-Agent": cfg.hh_user_agent,
        "Authorization": f"Bearer {token}",
    }
    resp = httpx.get(f"{cfg.hh_api_base}/vacancies/{vacancy_id}", headers=headers)
    resp.raise_for_status()
    return resp.json()


def build_cover_letter(vacancy: dict, resume_skills: set[str], cfg: Config) -> str:
    name = vacancy.get("name", "вакансия")
    employer = (vacancy.get("employer") or {}).get("name", "")
    requirements = (vacancy.get("snippet") or {}).get("requirement", "")
    responsibilities = (vacancy.get("snippet") or {}).get("responsibility", "")

    relevant_skills = [s for s in resume_skills if s.lower() in f"{name} {requirements} {responsibilities}".lower()]

    skills_text = ", ".join(relevant_skills[:6]) if relevant_skills else "Linux, Python, Docker, CI/CD, Ansible, автоматизация"

    letter = f"""Здравствуйте!

Меня заинтересовала вакансия «{name}» в компании {employer}.

Я — Linux-инженер с опытом администрирования 6+ лет. Работал с Proxmox, Docker, CI/CD (Woodpecker, GitLab CI), мониторингом (Prometheus/Grafana, Zabbix), автоматизацией на Python и Bash. Также имею опыт разработки на Rust (Axum, Actix-web).

Ключевые навыки подходящие под вакансию: {skills_text}.

Буду рад обсудить детали и возможность сотрудничества.

С уважением,
Максим Руденко
+7 (913) 750-31-88
t.me/techie88"""

    return letter


def run() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run --directory src python -m reply <vacancy_url>")
        sys.exit(1)

    url = sys.argv[1]
    vacancy_id = extract_vacancy_id(url)
    cfg = Config()
    resume_skills = load_resume_skills(cfg.resume_path)
    vacancy = get_vacancy_details(cfg, vacancy_id)

    letter = build_cover_letter(vacancy, resume_skills, cfg)

    print(f"\n{'='*70}")
    print(f"Vacancy: {vacancy.get('name')}")
    print(f"Company: {(vacancy.get('employer') or {}).get('name')}")
    print(f"URL:     {url}")
    print(f"{'='*70}\n")

    print("📝 Draft cover letter:\n")
    print(letter)
    print(f"\n{'='*70}")
    print("⚠️  This is a DRAFT. To send, we need a user OAuth token.")
    print("   (client_credentials token cannot send messages)")
    print(f"{'='*70}")


if __name__ == "__main__":
    run()
