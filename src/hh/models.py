from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Vacancy:
    id: int
    name: str
    alternate_url: str
    employer_name: str
    salary_from: int | None = None
    salary_to: int | None = None
    salary_currency: str | None = None
    requirement_raw: str | None = None
    responsibility_raw: str | None = None
    key_skills: list[str] = field(default_factory=list)
    area: str | None = None
    schedule: str | None = None
    experience: str | None = None
    employment: str | None = None

    @classmethod
    def from_api(cls, data: dict) -> Vacancy:
        salary = data.get("salary") or {}
        snippet = data.get("snippet") or {}
        skills = [s.get("name", "") for s in (data.get("key_skills") or [])]
        area = (data.get("area") or {}).get("name")
        schedule = (data.get("schedule") or {}).get("name")
        experience = (data.get("experience") or {}).get("name")
        employment = (data.get("employment") or {}).get("name")
        employer = (data.get("employer") or {}).get("name", "")
        return cls(
            id=int(data["id"]),
            name=data.get("name", ""),
            alternate_url=data.get("alternate_url", ""),
            employer_name=employer,
            salary_from=salary.get("from"),
            salary_to=salary.get("to"),
            salary_currency=salary.get("currency"),
            requirement_raw=snippet.get("requirement"),
            responsibility_raw=snippet.get("responsibility"),
            key_skills=skills,
            area=area,
            schedule=schedule,
            experience=experience,
            employment=employment,
        )
