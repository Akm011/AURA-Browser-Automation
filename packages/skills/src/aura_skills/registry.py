from __future__ import annotations

from aura_skills.base import BrowserSkill
from aura_skills.skills import WEEK2_SKILLS


class SkillRegistry:
    """Lookup table for browser skills by name."""

    def __init__(self, skills: list[type[BrowserSkill]] | None = None) -> None:
        skill_types = skills or WEEK2_SKILLS
        self._skills: dict[str, BrowserSkill] = {
            skill_type.name: skill_type() for skill_type in skill_types
        }

    def get(self, name: str) -> BrowserSkill | None:
        return self._skills.get(name)

    def list_names(self) -> list[str]:
        return sorted(self._skills.keys())

    def register(self, skill: BrowserSkill) -> None:
        self._skills[skill.name] = skill


def default_registry() -> SkillRegistry:
    return SkillRegistry()
