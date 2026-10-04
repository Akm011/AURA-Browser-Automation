from __future__ import annotations

from typing import Any

from aura_skills.base import BrowserSkill, SkillContext, SkillResult


class PressKey(BrowserSkill):
    name = "PressKey"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        key = kwargs.get("key")
        if not key:
            return SkillResult(success=False, message="Missing required param: key")
        await context.playwright_page.keyboard.press(str(key))
        return SkillResult(success=True, message=f"Pressed {key}", data={"key": str(key)})
