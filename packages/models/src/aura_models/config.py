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
    app_version: str = "0.0.1"
    log_level: str = "INFO"
    log_json: bool = False

    browser_headless: bool = False
    browser_timeout_ms: int = 30_000
    browser_slow_mo_ms: int = 0
    browser_channel: str | None = None

    screenshots_dir: Path = Field(default=Path("artifacts/screenshots"))
    downloads_dir: Path = Field(default=Path("artifacts/downloads"))
    logs_dir: Path = Field(default=Path("logs"))

    def ensure_directories(self) -> None:
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


def get_settings() -> AuraSettings:
    settings = AuraSettings()
    settings.ensure_directories()
    return settings
