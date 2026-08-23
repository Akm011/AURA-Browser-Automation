from __future__ import annotations

import re
import json
from datetime import UTC, datetime
from pathlib import Path

from playwright.async_api import BrowserContext


def session_key(session_id: str) -> str:
    """Return a filesystem-safe persistent session identifier."""
    key = re.sub(r"[^a-zA-Z0-9_-]+", "-", session_id).strip("-")
    if not key:
        raise ValueError("session_id must include at least one letter or number")
    return key


class SessionManager:
    """Loads and saves Playwright storage state for named browser sessions."""

    def __init__(self, sessions_dir: Path) -> None:
        self.sessions_dir = sessions_dir

    def state_path(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_key(session_id)}.json"

    def memory_path(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_key(session_id)}.memory.json"

    def context_options(self, session_id: str | None) -> dict[str, str]:
        if not session_id:
            return {}
        path = self.state_path(session_id)
        return {"storage_state": str(path)} if path.is_file() else {}

    async def save(self, context: BrowserContext, session_id: str | None) -> str | None:
        if not session_id:
            return None
        path = self.state_path(session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        await context.storage_state(path=str(path))
        return str(path)

    def load_memory(self, session_id: str | None) -> dict:
        if not session_id:
            return {"last_url": None, "completed_tasks": []}
        path = self.memory_path(session_id)
        if not path.is_file():
            return {"last_url": None, "completed_tasks": []}
        try:
            memory = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"last_url": None, "completed_tasks": []}
        if not isinstance(memory, dict):
            return {"last_url": None, "completed_tasks": []}
        return memory

    def record_completion(
        self,
        session_id: str | None,
        *,
        url: str,
        skills: list[str],
        success: bool,
    ) -> None:
        if not session_id:
            return
        memory = self.load_memory(session_id)
        tasks = memory.get("completed_tasks", [])
        if not isinstance(tasks, list):
            tasks = []
        tasks.append(
            {
                "completed_at": datetime.now(UTC).isoformat(),
                "url": url,
                "skills": skills,
                "success": success,
            }
        )
        memory["last_url"] = url
        memory["completed_tasks"] = tasks[-20:]
        path = self.memory_path(session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(memory, indent=2), encoding="utf-8")
