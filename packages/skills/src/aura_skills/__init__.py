"""Reusable browser skills framework (Week 2)."""

from aura_skills.base import BrowserSkill, SkillContext, SkillResult
from aura_skills.executor import ActionExecutor
from aura_skills.registry import SkillRegistry, default_registry

__all__ = [
    "ActionExecutor",
    "BrowserSkill",
    "SkillContext",
    "SkillRegistry",
    "SkillResult",
    "default_registry",
]
