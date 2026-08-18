from __future__ import annotations

from typing import Any

from aura_skills.base import BrowserSkill, SkillContext, SkillResult
from aura_skills.helpers import resolve_locator


class ClickElement(BrowserSkill):
    name = "ClickElement"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        page = context.playwright_page
        locator = await resolve_locator(
            page,
            text=kwargs.get("text"),
            selector=kwargs.get("selector"),
        )
        if locator is None:
            return SkillResult(success=False, message="Could not locate element to click")

        await locator.click()
        return SkillResult(
            success=True,
            message="Element clicked",
            data={"text": kwargs.get("text"), "selector": kwargs.get("selector")},
        )
