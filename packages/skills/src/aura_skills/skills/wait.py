from __future__ import annotations

import asyncio
from typing import Any

from aura_skills.base import BrowserSkill, SkillContext, SkillResult


class Wait(BrowserSkill):
    name = "Wait"

    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        raw_seconds = kwargs.get("seconds")
        if raw_seconds is None:
            return SkillResult(success=False, message="Missing required param: seconds")

        seconds = float(raw_seconds)
        if seconds < 0:
            return SkillResult(success=False, message="Wait duration must be non-negative")

        await asyncio.sleep(seconds)
        return SkillResult(
            success=True,
            message=f"Waited {seconds} seconds",
            data={"seconds": seconds},
        )
