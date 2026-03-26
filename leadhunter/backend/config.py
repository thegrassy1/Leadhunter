"""Application settings and constants."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent
# Default: ../data from backend/ (leadhunter/data/). Override in Docker: LEADHUNTER_DATA_DIR=/app/data
DATA_DIR = Path(os.environ.get("LEADHUNTER_DATA_DIR", str(BACKEND_DIR.parent / "data")))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = f"sqlite+aiosqlite:///{DATA_DIR / 'leadhunter.db'}"
    scrape_rate_limit: float = 4.0
    log_level: str = "INFO"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    apollo_api_key: str = ""

    gmail_credentials_path: str = "credentials/credentials.json"
    gmail_token_path: str = "credentials/token.json"
    gmail_poll_interval: int = 60

    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost,http://127.0.0.1"
    )


settings = Settings()


def get_cors_origins() -> list[str]:
    return [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
