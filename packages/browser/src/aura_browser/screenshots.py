from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from playwright.async_api import Page

from aura_browser.sessions import session_key


class ScreenshotService:
    """Captures full-page screenshots in a predictable artifact directory."""

    def __init__(self, screenshots_dir: Path) -> None:
        self.screenshots_dir = screenshots_dir

    async def capture(self, page: Page, *, session_id: str, label: str = "page") -> str:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        filename = f"{session_key(label)}-{timestamp}.png"
        path = self.screenshots_dir / session_key(session_id) / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(path), full_page=True)
        return str(path)
