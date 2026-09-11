from __future__ import annotations

from collections import Counter
from typing import Iterable


def aggregate_key_errors(sessions: Iterable[dict]) -> dict[str, int]:
    totals: Counter[str] = Counter()
    for session in sessions:
        errors = session.get("key_errors", {})
        if isinstance(errors, dict):
            for key, count in errors.items():
                try:
                    totals[str(key)] += max(0, int(count))
                except (TypeError, ValueError):
                    continue
    return dict(totals.most_common())


def averages(sessions: Iterable[dict]) -> dict[str, float]:
    rows = list(sessions)
    if not rows:
        return {"wpm": 0.0, "cpm": 0.0, "accuracy": 0.0, "errors": 0.0}
    return {
        "wpm": sum(float(r.get("wpm", 0)) for r in rows) / len(rows),
        "cpm": sum(float(r.get("cpm", 0)) for r in rows) / len(rows),
        "accuracy": sum(float(r.get("accuracy", 0)) for r in rows) / len(rows),
        "errors": sum(float(r.get("errors", 0)) for r in rows) / len(rows),
    }


def best_by(sessions: Iterable[dict], metric: str) -> dict | None:
    rows = list(sessions)
    if not rows:
        return None
    return max(rows, key=lambda row: float(row.get(metric, 0)))
