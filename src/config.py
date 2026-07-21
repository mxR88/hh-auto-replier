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
    access_token: str = os.getenv("HH_ACCESS_TOKEN", "")
    refresh_token: str = os.getenv("HH_REFRESH_TOKEN", "")

    search_text: str = "Linux DevOps SRE инженер"
    search_area: list[int] = field(default_factory=lambda: [1, 113])
    exclude_words: list[str] = field(default_factory=lambda: ["Windows", "Microsoft", "1C"])
    search_per_page: int = 50
    search_schedule: str = "remote"

    salary_from: int = 150_000

    hh_api_base: str = "https://api.hh.ru"
    hh_user_agent: str = "HH-Rust-Bot/1.0 (https://t.me/rust_hh_jobs_bot)"

    resume_path: str = str(Path(__file__).resolve().parent.parent / "resume.html")

    def __post_init__(self) -> None:
        if not self.client_id or not self.client_secret:
            raise ValueError("HH_CLIENT_ID and HH_CLIENT_SECRET must be set in .env")
