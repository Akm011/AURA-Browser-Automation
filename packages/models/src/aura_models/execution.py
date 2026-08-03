from datetime import datetime, timezone

from pydantic import BaseModel, Field, HttpUrl


class BrowserSession(BaseModel):
    session_id: str
    url: HttpUrl
    title: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LaunchResult(BaseModel):
    success: bool
    session: BrowserSession | None = None
    screenshot_path: str | None = None
    error: str | None = None
