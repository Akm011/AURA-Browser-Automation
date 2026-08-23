from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuraSettings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="AURA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AURA Browser Intelligence Core"
    app_version: str = "0.2.1"
    log_level: str = "INFO"
    log_json: bool = False
    cors_origins: list[str] = Field(default=["http://localhost:8000", "http://127.0.0.1:8000"])

    browser_headless: bool = True
    browser_timeout_ms: int = 30_000
    browser_slow_mo_ms: int = 0
    browser_step_delay_seconds: float = Field(default=0.0, ge=0)
    browser_channel: str | None = None

    screenshots_dir: Path = Field(default=Path("artifacts/screenshots"))
    sessions_dir: Path = Field(default=Path("artifacts/sessions"))
    downloads_dir: Path = Field(default=Path("artifacts/downloads"))
    logs_dir: Path = Field(default=Path("logs"))

    def ensure_directories(self) -> None:
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


def get_settings() -> AuraSettings:
    settings = AuraSettings()
    settings.ensure_directories()
    return settings
