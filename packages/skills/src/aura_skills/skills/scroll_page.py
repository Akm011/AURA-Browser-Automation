from __future__ import annotations

from typing import Any

from aura_skills.base import BrowserSkill, SkillContext, SkillResult


class ScrollPage(BrowserSkill):
    name = "ScrollPage"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        pixels = int(kwargs.get("pixels", 600))
        await context.playwright_page.mouse.wheel(0, pixels)
        return SkillResult(success=True, message=f"Scrolled {pixels} pixels", data={"pixels": pixels})
