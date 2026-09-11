from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class Lesson:
    id: str
    title: str
    level: str
    language: str
    text: str
    hint: str


RUSSIAN_LESSONS = [
    Lesson("ru-home-left", "Левая рука", "Начальный", "Русский", "фыва фыва ыва фа", "Учимся возвращать пальцы на ФЫВА."),
    Lesson("ru-home-right", "Правая рука", "Начальный", "Русский", "олдж олдж олд ож", "Учимся возвращать пальцы на ОЛДЖ."),
    Lesson("ru-home", "Домашний ряд", "Начальный", "Русский", "фыва олдж фыва олдж", "Чередуйте левую и правую руку."),
    Lesson("ru-top", "Верхний ряд", "Начальный", "Русский", "йцуке нгшщз хъ", "Переходите вверх и возвращайтесь домой."),
    Lesson("ru-bottom", "Нижний ряд", "Начальный", "Русский", "ячсмитьбю ячсмитьбю", "Не смотрите на клавиши."),
    Lesson("ru-words", "Простые слова", "Средний", "Русский", "мир дом лес вода книга", "Сохраняйте ровный ритм."),
    Lesson("ru-phrases", "Предложения", "Средний", "Русский", "точность важнее скорости", "Сначала точность, потом скорость."),
    Lesson("ru-advanced", "Связный текст", "Продвинутый", "Русский", "Регулярная спокойная тренировка помогает уверенно печатать вслепую.", "Работайте без рывков."),
]

ENGLISH_LESSONS = [
    Lesson("en-home", "Home row", "Начальный", "English", "asdf jkl; asdf jkl;", "Keep both hands on the home row."),
    Lesson("en-top", "Top row", "Начальный", "English", "qwer uiop qwer uiop", "Move up and return to the home row."),
    Lesson("en-bottom", "Bottom row", "Начальный", "English", "zxcv nm,. zxcv nm,.", "Type slowly without looking down."),
    Lesson("en-words", "Simple words", "Средний", "English", "home work time book", "Keep a steady rhythm."),
    Lesson("en-phrases", "Sentences", "Средний", "English", "accuracy matters more than speed", "Accuracy comes first."),
    Lesson("en-advanced", "Connected text", "Продвинутый", "English", "Regular calm practice makes blind typing easier and more reliable.", "Avoid rushing."),
]

ALL_LESSONS = RUSSIAN_LESSONS + ENGLISH_LESSONS


def lessons(language: str, level: str | None = None) -> list[Lesson]:
    result = [item for item in ALL_LESSONS if item.language == language]
    if level:
        result = [item for item in result if item.level == level]
    return result


def random_lesson(language: str, level: str) -> Lesson:
    options = lessons(language, level)
    if not options:
        options = lessons(language)
    if not options:
        raise ValueError(f"No lessons for language={language!r}")
    return random.choice(options)
