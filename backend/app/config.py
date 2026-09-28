import secrets
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    database_url: str = "sqlite:///./clinical.db"
    session_secret: str = ""
    ai_api_key: str = ""
    ai_model: str = "gpt-4.1-mini"
    app_origin: str = "http://127.0.0.1:8000"
    environment: str = "development"
    upload_dir: Path = ROOT / "uploads"
    frontend_dir: Path = ROOT / "frontend" / "dist"
    max_upload_bytes: int = 10 * 1024 * 1024
    max_text_chars: int = 20000
    max_pdf_pages: int = 10
    max_pending_jobs: int = 8
    submissions_per_hour: int = 10
    global_submissions_per_hour: int = 50
    job_timeout_seconds: int = 300

    @model_validator(mode="after")
    def validate_environment(self):
        if self.environment == "production":
            if len(self.session_secret) < 32:
                raise ValueError(
                    "Production requires SESSION_SECRET of at least 32 characters."
                )
            if not self.app_origin.startswith("https://"):
                raise ValueError("Production requires an HTTPS APP_ORIGIN.")
        elif not self.session_secret:
            self.session_secret = secrets.token_urlsafe(32)
        return self
