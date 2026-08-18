from __future__ import annotations

from typing import Any

from aura_skills.base import BrowserSkill, SkillContext, SkillResult
from aura_skills.helpers import resolve_input


class FillInput(BrowserSkill):
    name = "FillInput"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        page = context.playwright_page
        value = kwargs.get("value")
        if value is None:
            return SkillResult(success=False, message="Missing required param: value")

        locator = await resolve_input(
            page,
            label=kwargs.get("label"),
            placeholder=kwargs.get("placeholder"),
            name=kwargs.get("name"),
            selector=kwargs.get("selector"),
        )
        if locator is None:
            return SkillResult(success=False, message="Could not locate input field")

        await locator.fill(str(value))
        return SkillResult(
            success=True,
            message=f"Filled input with value",
            data={"value_length": len(str(value))},
        )
