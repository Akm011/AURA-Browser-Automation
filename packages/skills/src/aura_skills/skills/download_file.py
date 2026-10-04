from __future__ import annotations

from typing import Any

from aura_skills.base import BrowserSkill, SkillContext, SkillResult
from aura_skills.helpers import resolve_locator


class DownloadFile(BrowserSkill):
    name = "DownloadFile"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        locator = await resolve_locator(
            context.playwright_page,
            text=kwargs.get("text"),
            selector=kwargs.get("selector"),
        )
        if locator is None:
            return SkillResult(success=False, message="Could not locate download element")
        async with context.playwright_page.expect_download() as download_info:
            await locator.click()
        download = await download_info.value
        path = context.settings.downloads_dir / download.suggested_filename
        await download.save_as(str(path))
        return SkillResult(
            success=True,
            message="Download completed",
            data={"path": str(path), "filename": download.suggested_filename},
        )
