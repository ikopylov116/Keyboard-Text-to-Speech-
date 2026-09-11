from __future__ import annotations


class AccessibilityController:
    """Keyboard-first accessibility policy for blind and low-vision users."""

    def __init__(self, speech, store):
        self.speech = speech
        self.store = store
        self.enabled = bool(store.get_setting("speech_enabled", True))
        self.speak_characters = bool(store.get_setting("speak_characters", False))
        self.speak_errors = bool(store.get_setting("speak_errors", True))
        self.speech.set_enabled(self.enabled)

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        self.speech.set_enabled(self.enabled)
        self.store.set_setting("speech_enabled", self.enabled)
        self.speak("Озвучка включена" if self.enabled else "Озвучка выключена")
        return self.enabled

    def speak(self, text: str) -> None:
        if self.enabled:
            self.speech.say(text)

    def character_feedback(self, char: str, correct: bool, expected: str | None) -> None:
        if not self.enabled:
            return
        if correct and self.speak_characters:
            self.speech.say(self.describe_char(char))
        elif not correct and self.speak_errors:
            expected_text = self.describe_char(expected) if expected else "конец задания"
            self.speech.say(f"Ошибка. Нужно: {expected_text}")

    @staticmethod
    def describe_char(char: str | None) -> str:
        if not char:
            return ""
        names = {
            " ": "пробел", "\n": "новая строка", "\t": "табуляция",
            ".": "точка", ",": "запятая", "!": "восклицательный знак",
            "?": "вопросительный знак", ":": "двоеточие", ";": "точка с запятой",
            "-": "дефис", "_": "подчёркивание", "[": "левая квадратная скобка",
            "]": "правая квадратная скобка", "'": "апостроф",
        }
        return names.get(char, char)

    def save_preferences(self) -> None:
        self.store.set_setting("speech_enabled", self.enabled)
        self.store.set_setting("speak_characters", self.speak_characters)
        self.store.set_setting("speak_errors", self.speak_errors)
