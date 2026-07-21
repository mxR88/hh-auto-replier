from __future__ import annotations

import httpx

from config import Config


class HHClient:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        token = cfg.access_token or self._get_app_token()
        self._client = httpx.Client(
            base_url=cfg.hh_api_base,
            headers={
                "User-Agent": cfg.hh_user_agent,
                "Authorization": f"Bearer {token}",
            },
        )

    def _get_app_token(self) -> str:
        resp = httpx.post(
            f"{self.cfg.hh_api_base}/token",
            headers={"User-Agent": self.cfg.hh_user_agent},
            data={
                "grant_type": "client_credentials",
                "client_id": self.cfg.client_id,
                "client_secret": self.cfg.client_secret,
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def search_vacancies(self, text: str = "", page: int = 0) -> dict:
        params: dict = {
            "text": text or self.cfg.search_text,
            "area": self.cfg.search_area[0],
            "schedule": self.cfg.search_schedule,
            "salary_from": self.cfg.salary_from,
            "per_page": self.cfg.search_per_page,
            "page": page,
            "only_with_salary": True,
        }
        resp = self._client.get("/vacancies", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_vacancy(self, vacancy_id: str | int) -> dict:
        resp = self._client.get(f"/vacancies/{vacancy_id}")
        resp.raise_for_status()
        return resp.json()
