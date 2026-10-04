from __future__ import annotations

from typing import Any

from aura_skills.base import BrowserSkill, SkillContext, SkillResult


class UploadFile(BrowserSkill):
    name = "UploadFile"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        path = kwargs.get("path")
        if not path:
            return SkillResult(success=False, message="Missing required param: path")
        selector = str(kwargs.get("selector", "input[type='file']"))
        locator = context.playwright_page.locator(selector)
        if await locator.count() == 0:
            return SkillResult(success=False, message="No file input found")
        await locator.first.set_input_files(str(path))
        return SkillResult(success=True, message="File selected", data={"path": str(path)})
