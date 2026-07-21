from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    client_id: str = os.getenv("HH_CLIENT_ID", "")
    client_secret: str = os.getenv("HH_CLIENT_SECRET", "")
    redirect_uri: str = os.getenv("HH_REDIRECT_URI", "")
    app_token: str = os.getenv("HH_APP_TOKEN", "")
    user_token: str = os.getenv("HH_USER_TOKEN", "")
    refresh_token: str = os.getenv("HH_REFRESH_TOKEN", "")

    @property
    def access_token(self) -> str:
        return self.app_token

    search_text: str = "Linux OR DevOps OR SRE OR \"системный администратор\""
    search_area: list[int] = field(default_factory=lambda: [1])
    exclude_words: list[str] = field(default_factory=lambda: ["Windows", "Microsoft", "1C", "ad", "embedded", "kernel", "драйвер", "1с", "менеджер", "тренер", "воспитатель", "специалист по закупкам"])
    search_per_page: int = 100
    search_schedule: str = ""

    salary_from: int = 150000

    hh_api_base: str = "https://api.hh.ru"
    hh_user_agent: str = "HH-Rust-Bot/1.0 (https://t.me/rust_hh_jobs_bot)"

    resume_path: str = str(Path(__file__).resolve().parent.parent / "resume.html")

    def __post_init__(self) -> None:
        if not self.client_id or not self.client_secret:
            raise ValueError("HH_CLIENT_ID and HH_CLIENT_SECRET must be set in .env")
