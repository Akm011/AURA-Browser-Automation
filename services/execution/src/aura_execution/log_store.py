from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aura_browser.sessions import session_key

from aura_execution.task_store import TaskRecord


class LogStore:
    """Persist the latest execution record for each task, grouped by session."""

    def __init__(self, logs_dir: Path) -> None:
        self.logs_dir = logs_dir

    def save(self, task: TaskRecord) -> None:
        session_id = task.session_id or task.id
        path = self._path(session_id)
        entries = self._read(path)
        entry = task.model_dump(mode="json")
        entry["session_id"] = session_id
        entries = [item for item in entries if item.get("id") != task.id]
        entries.append(entry)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(entries, indent=2), encoding="utf-8")

    def list(self, session_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        paths = [self._path(session_id)] if session_id else self.logs_dir.glob("*.json")
        entries = [entry for path in paths for entry in self._read(path)]
        entries.sort(key=lambda entry: entry.get("created_at", ""), reverse=True)
        return entries[:limit]

    def _path(self, session_id: str) -> Path:
        return self.logs_dir / f"{session_key(session_id)}.json"

    @staticmethod
    def _read(path: Path) -> list[dict[str, Any]]:
        if not path.is_file():
            return []
        try:
            content = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return content if isinstance(content, list) else []
