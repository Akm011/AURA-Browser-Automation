from __future__ import annotations

from typing import Any

from aura_skills.base import BrowserSkill, SkillContext, SkillResult


class ExtractText(BrowserSkill):
    name = "ExtractText"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        selector = str(kwargs.get("selector", "body"))
        locator = context.playwright_page.locator(selector)
        if await locator.count() == 0:
            return SkillResult(success=False, message=f"Could not locate {selector}")
        text = (await locator.first.inner_text()).strip()
        return SkillResult(
            success=True,
            message="Extracted page text",
            data={"text": text[:10_000], "truncated": len(text) > 10_000},
        )
