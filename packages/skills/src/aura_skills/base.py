from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from playwright.async_api import Page
from pydantic import BaseModel, Field

from aura_models.config import AuraSettings


class SkillContext(BaseModel):
    page: Any = Field(exclude=True)
    settings: AuraSettings

    model_config = {"arbitrary_types_allowed": True}

    @property
    def playwright_page(self) -> Page:
        return self.page


class SkillResult(BaseModel):
    success: bool
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class BrowserSkill(ABC):
    """Base class for reusable browser skills."""

    name: str

    @abstractmethod
    async def execute(self, context: SkillContext, **kwargs: Any) -> SkillResult:
        raise NotImplementedError
