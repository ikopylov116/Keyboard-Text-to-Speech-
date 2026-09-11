from __future__ import annotations

RUSSIAN_ROWS = (
    "йцукенгшщзхъ",
    "фывапролджэ",
    "ячсмитьбю",
)
ENGLISH_ROWS = (
    "qwertyuiop[]",
    "asdfghjkl;'",
    "zxcvbnm,./",
)


def rows(language: str) -> tuple[str, ...]:
    if language == "English":
        return ENGLISH_ROWS
    return RUSSIAN_ROWS


def finger_hint(language: str, char: str) -> str:
    c = char.lower()
    layout = rows(language)
    positions = {key: (row, i) for row, line in enumerate(layout) for i, key in enumerate(line)}
    item = positions.get(c)
    if item is None:
        return ""
    row, col = item
    if language == "English":
        left = (row == 0 and col <= 4) or (row > 0 and col <= 3)
        names = ["мизинец", "безымянный", "средний", "указательный"]
    else:
        left = (row == 0 and col <= 5) or (row > 0 and col <= 4)
        names = ["мизинец", "безымянный", "средний", "указательный"]
    finger = names[min(col, 3)] if left else names[min(max(len(layout[row]) - col - 1, 0), 3)]
    hand = "левой" if left else "правой"
    return f"{finger} палец {hand} руки"
