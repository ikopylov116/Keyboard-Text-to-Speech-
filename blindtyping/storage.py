from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .engine import TypingResult


class HistoryStore:
    """Small local JSON database; no cloud, account or AI service is required."""

    def __init__(self, path: Path | None = None):
        self.path = path or (Path.home() / ".blindtyping" / "history.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"sessions": [], "settings": {}}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError
            data.setdefault("sessions", [])
            data.setdefault("settings", {})
            return data
        except (OSError, ValueError, json.JSONDecodeError):
            return {"sessions": [], "settings": {}}

    def _save(self) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def add_result(self, result: TypingResult, level: str) -> None:
        self._data["sessions"].append({
            "level": level,
            "target": result.target,
            "typed": result.typed,
            "elapsed": round(result.elapsed, 3),
            "errors": result.errors,
            "correct_chars": result.correct_chars,
            "total_chars": result.total_chars,
            "accuracy": round(result.accuracy, 2),
            "cpm": round(result.cpm, 2),
            "wpm": round(result.wpm, 2),
            "key_errors": result.key_errors,
        })
        self._data["sessions"] = self._data["sessions"][-200:]
        self._save()

    def sessions(self) -> list[dict[str, Any]]:
        return list(self._data["sessions"])

    def best(self) -> dict[str, float]:
        rows = self.sessions()
        if not rows:
            return {"wpm": 0.0, "accuracy": 0.0, "sessions": 0}
        return {
            "wpm": max(float(r.get("wpm", 0)) for r in rows),
            "accuracy": max(float(r.get("accuracy", 0)) for r in rows),
            "sessions": len(rows),
        }

    def set_setting(self, key: str, value: Any) -> None:
        self._data["settings"][key] = value
        self._save()

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self._data["settings"].get(key, default)
