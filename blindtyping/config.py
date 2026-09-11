from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


APP_NAME = "BlindTyping"
DATA_DIR = Path.home() / ".blindtyping"
HISTORY_FILE = DATA_DIR / "history.json"
MAX_HISTORY = 500


@dataclass(frozen=True)
class SpeechConfig:
    enabled: bool = True
    rate: int = 175
    volume: float = 1.0
    speak_characters: bool = True
    speak_errors: bool = True


@dataclass(frozen=True)
class TrainingConfig:
    language: str = "Русский"
    level: str = "Начальный"
    allow_backspace: bool = True
    repeat_mistakes: bool = False


MIN_SPEECH_RATE = 80
MAX_SPEECH_RATE = 260
MIN_VOLUME = 0.0
MAX_VOLUME = 1.0
