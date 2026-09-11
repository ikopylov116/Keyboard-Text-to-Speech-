from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import time


@dataclass(frozen=True)
class TypingResult:
    target: str
    typed: str
    elapsed: float
    errors: int
    correct_chars: int
    total_chars: int
    accuracy: float
    cpm: float
    wpm: float
    key_errors: dict[str, int] = field(default_factory=dict)


class TypingSession:
    """Pure, deterministic typing state. No UI, TTS, files or network access."""

    def __init__(self, target: str, allow_backspace: bool = True):
        if not target:
            raise ValueError("target must not be empty")
        self.target = target
        self.allow_backspace = allow_backspace
        self.typed = ""
        self.started_at: float | None = None
        self.finished_at: float | None = None
        self.key_errors: Counter[str] = Counter()
        self.total_keystrokes = 0

    @property
    def running(self) -> bool:
        return self.started_at is not None and self.finished_at is None

    @property
    def finished(self) -> bool:
        return self.finished_at is not None

    @property
    def position(self) -> int:
        return len(self.typed)

    @property
    def expected(self) -> str | None:
        if self.position >= len(self.target):
            return None
        return self.target[self.position]

    def start(self) -> None:
        if self.started_at is None:
            self.started_at = time.perf_counter()

    def reset(self, target: str | None = None) -> None:
        if target is not None:
            if not target:
                raise ValueError("target must not be empty")
            self.target = target
        self.typed = ""
        self.started_at = None
        self.finished_at = None
        self.key_errors.clear()
        self.total_keystrokes = 0

    def add_char(self, char: str) -> bool:
        if len(char) != 1 or self.finished:
            return False
        self.start()
        expected = self.expected
        correct = expected == char
        self.total_keystrokes += 1
        if not correct:
            self.key_errors[char] += 1
        self.typed += char
        if self.position >= len(self.target):
            self.finished_at = time.perf_counter()
        return correct

    def backspace(self) -> bool:
        if not self.allow_backspace or not self.typed or self.finished:
            return False
        self.typed = self.typed[:-1]
        return True

    def elapsed(self) -> float:
        if self.started_at is None:
            return 0.0
        end = self.finished_at or time.perf_counter()
        return max(0.001, end - self.started_at)

    def result(self) -> TypingResult:
        total = len(self.target)
        correct = sum(a == b for a, b in zip(self.target, self.typed))
        errors = max(0, len(self.typed) - correct) + max(0, total - len(self.typed))
        elapsed = self.elapsed()
        accuracy = (correct / len(self.typed) * 100) if self.typed else (100.0 if not self.started_at else 0.0)
        cpm = correct / elapsed * 60 if self.started_at else 0.0
        return TypingResult(
            target=self.target,
            typed=self.typed,
            elapsed=elapsed,
            errors=errors,
            correct_chars=correct,
            total_chars=total,
            accuracy=accuracy,
            cpm=cpm,
            wpm=cpm / 5,
            key_errors=dict(self.key_errors),
        )
