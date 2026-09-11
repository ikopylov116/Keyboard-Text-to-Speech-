from __future__ import annotations

from dataclasses import dataclass, field
import time
from collections import Counter


@dataclass
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
    """Pure typing logic. UI and speech are deliberately kept outside this class."""

    def __init__(self, target: str):
        self.target = target
        self.typed = ""
        self.started_at: float | None = None
        self.finished_at: float | None = None
        self.key_errors: Counter[str] = Counter()

    @property
    def running(self) -> bool:
        return self.started_at is not None and self.finished_at is None

    @property
    def finished(self) -> bool:
        return self.finished_at is not None

    def start(self) -> None:
        if self.started_at is None:
            self.started_at = time.perf_counter()

    def reset(self, target: str | None = None) -> None:
        if target is not None:
            self.target = target
        self.typed = ""
        self.started_at = None
        self.finished_at = None
        self.key_errors.clear()

    def add_char(self, char: str) -> bool:
        if not char or self.finished:
            return False
        self.start()
        position = len(self.typed)
        expected = self.target[position] if position < len(self.target) else None
        if expected != char:
            self.key_errors[char] += 1
        self.typed += char
        if len(self.typed) >= len(self.target):
            self.finished_at = time.perf_counter()
        return expected == char

    def backspace(self) -> None:
        if self.typed and not self.finished:
            self.typed = self.typed[:-1]

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
        accuracy = (correct / total * 100) if total else 100.0
        cpm = correct / elapsed * 60 if elapsed else 0.0
        wpm = cpm / 5
        return TypingResult(
            target=self.target,
            typed=self.typed,
            elapsed=elapsed,
            errors=errors,
            correct_chars=correct,
            total_chars=total,
            accuracy=accuracy,
            cpm=cpm,
            wpm=wpm,
            key_errors=dict(self.key_errors),
        )


RUSSIAN_TEXTS = [
    "Начинайте печатать спокойно и не смотрите на клавиатуру.",
    "Точная печать важнее высокой скорости на первых занятиях.",
    "Регулярная короткая тренировка помогает уверенно запомнить расположение клавиш.",
    "Старайтесь держать пальцы в исходной позиции и возвращать их после каждого нажатия.",
]

ENGLISH_TEXTS = [
    "Start typing slowly and keep your eyes away from the keyboard.",
    "Accuracy is more important than speed when you are learning to type.",
    "Regular short practice makes keyboard positions easier to remember.",
    "Keep your fingers on the home row and return them after each key press.",
]

LEVELS = {
    "Начальный": ["фыва", "олдж", "фыва олдж", "ыва олд", "фыва олдж фыва"],
    "Средний": ["привет мир", "быстрая печать", "точность важнее скорости"],
    "Продвинутый": RUSSIAN_TEXTS,
}
