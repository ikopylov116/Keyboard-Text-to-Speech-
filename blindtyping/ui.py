from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .analytics import aggregate_key_errors, averages
from .content import lessons, random_lesson
from .engine import TypingSession
from .keyboard_layout import finger_hint, rows
from .speech import SpeechService
from .storage import HistoryStore


class BlindTypingUI(tk.Tk):
    """Presentation layer. Training rules live in engine/content; persistence in storage."""

    BG = "#10131a"
    PANEL = "#191e28"
    INPUT = "#11151c"
    TEXT = "#f2f4f8"
    MUTED = "#9aa4b2"
    ACCENT = "#6ea8fe"
    GOOD = "#72d6a5"
    BAD = "#ff7b7b"

    def __init__(self):
        super().__init__()
        self.title("BlindTyping — тренажёр слепой печати")
        self.geometry("1180x780")
        self.minsize(960, 680)
        self.configure(bg=self.BG)
        self.store = HistoryStore()
        self.speech = SpeechService(
            rate=int(self.store.get_setting("speech_rate", 175)),
            volume=float(self.store.get_setting("speech_volume", 1.0)),
        )
        self.language = str(self.store.get_setting("language", "Русский"))
        self.level = str(self.store.get_setting("level", "Начальный"))
        self.session = TypingSession(random_lesson(self.language, self.level).text)
        self.lesson = None
        self.entry: tk.Text | None = None
        self.target: tk.Text | None = None
        self.status = tk.StringVar(value="Готово")
        self._style()
        self._shell()
        self.show_home()
        self.protocol("WM_DELETE_WINDOW", self.close)

    def _style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", background=self.PANEL, foreground=self.TEXT,
                        fieldbackground=self.PANEL, rowheight=30)
        style.configure("Treeview.Heading", background="#252c38", foreground=self.TEXT,
                        relief="flat", font=("Segoe UI", 10, "bold"))

    def _shell(self):
        header = tk.Frame(self, bg=self.PANEL)
        header.pack(fill="x")
        tk.Label(header, text="⌨ BlindTyping", bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 21, "bold")).pack(side="left", padx=24, pady=15)
        tk.Label(header, text="офлайн • без ИИ • модульная архитектура",
                 bg=self.PANEL, fg=self.MUTED).pack(side="left")
        nav = tk.Frame(self, bg="#141820", width=215)
        nav.pack(side="left", fill="y")
        for key, title in (("home", "Главная"), ("train", "Уроки и тренировка"),
                           ("free", "Свободная печать"), ("stats", "Статистика"),
                           ("settings", "Настройки")):
            tk.Button(nav, text=title, anchor="w", bd=0, padx=20, pady=13,
                      bg="#141820", fg=self.TEXT, activebackground="#252d3a",
                      activeforeground=self.TEXT, font=("Segoe UI", 11),
                      command=lambda k=key: self.navigate(k)).pack(fill="x", padx=10, pady=3)
        tk.Label(nav, text="\nПринцип\nТочность → ритм → скорость\n\nНе смотрите на клавиатуру.",
                 bg="#141820", fg=self.MUTED, justify="left", anchor="w",
                 font=("Segoe UI", 9)).pack(fill="x", padx=20, pady=18)
        self.content = tk.Frame(self, bg=self.BG)
        self.content.pack(side="left", fill="both", expand=True)

    def navigate(self, page):
        {"home": self.show_home, "train": self.show_train, "free": self.show_free,
         "stats": self.show_stats, "settings": self.show_settings}[page]()

    def _clear(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        self.entry = None
        self.target = None

    def _heading(self, title, subtitle=""):
        tk.Label(self.content, text=title, bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 25, "bold")).pack(anchor="w", padx=32, pady=(28, 4))
        if subtitle:
            tk.Label(self.content, text=subtitle, bg=self.BG, fg=self.MUTED,
                     font=("Segoe UI", 11)).pack(anchor="w", padx=34, pady=(0, 18))

    def _button(self, parent, text, command):
        return tk.Button(parent, text=text, command=command, bd=0, padx=17, pady=10,
                         bg="#2a6fdb", fg="white", activebackground="#3d82ed",
                         activeforeground="white", font=("Segoe UI", 10, "bold"), cursor="hand2")

    def show_home(self):
        self._clear(); self._heading("Главная", "Постепенное обучение слепой печати с голосовой обратной связью")
        best = self.store.best(); avg = averages(self.store.sessions())
        cards = tk.Frame(self.content, bg=self.BG); cards.pack(fill="x", padx=32)
        for title, value in (("Тренировок", str(int(best["sessions"]))),
                             ("Лучший WPM", f"{best['wpm']:.0f}"),
                             ("Средний WPM", f"{avg['wpm']:.0f}"),
                             ("Средняя точность", f"{avg['accuracy']:.1f}%")):
            box = tk.Frame(cards, bg=self.PANEL, padx=18, pady=16)
            box.pack(side="left", fill="both", expand=True, padx=(0, 10))
            tk.Label(box, text=title, bg=self.PANEL, fg=self.MUTED).pack(anchor="w")
            tk.Label(box, text=value, bg=self.PANEL, fg=self.TEXT,
                     font=("Segoe UI", 21, "bold")).pack(anchor="w", pady=4)
        box = tk.Frame(self.content, bg=self.PANEL, padx=24, pady=24)
        box.pack(fill="x", padx=32, pady=24)
        tk.Label(box, text="Учимся правильно", bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(box, text="Система ведёт от домашних клавиш к словам и предложениям. Ошибки фиксируются по клавишам, а результаты сохраняются локально.",
                 bg=self.PANEL, fg=self.MUTED, wraplength=800, justify="left").pack(anchor="w", pady=8)
        self._button(box, "Начать урок", self.show_train).pack(anchor="w", pady=8)

    def show_train(self):
        self._clear(); self._heading("Уроки и тренировка", "Выберите язык и уровень, затем выполните упражнение")
        controls = tk.Frame(self.content, bg=self.BG); controls.pack(fill="x", padx=32)
        tk.Label(controls, text="Язык", bg=self.BG, fg=self.MUTED).pack(side="left")
        lang = tk.StringVar(value=self.language)
        ttk.Combobox(controls, textvariable=lang, values=("Русский", "English"), state="readonly", width=12).pack(side="left", padx=8)
        tk.Label(controls, text="Уровень", bg=self.BG, fg=self.MUTED).pack(side="left", padx=(16, 0))
        level = tk.StringVar(value=self.level)
        ttk.Combobox(controls, textvariable=level, values=("Начальный", "Средний", "Продвинутый"), state="readonly", width=16).pack(side="left", padx=8)
        self._button(controls, "Новое упражнение", lambda: self._start_lesson(lang.get(), level.get())).pack(side="left", padx=8)
        self._build_lesson()

    def _start_lesson(self, language=None, level=None):
        self.language = language or self.language; self.level = level or self.level
        self.lesson = random_lesson(self.language, self.level)
        self.session.reset(self.lesson.text)
        self.show_train()

    def _build_lesson(self):
        if self.lesson is None:
            self.lesson = random_lesson(self.language, self.level)
            self.session.reset(self.lesson.text)
        panel = tk.Frame(self.content, bg=self.PANEL, padx=22, pady=20)
        panel.pack(fill="both", expand=True, padx=32, pady=20)
        tk.Label(panel, text=self.lesson.title, bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(panel, text=self.lesson.hint, bg=self.PANEL, fg=self.MUTED).pack(anchor="w", pady=(2, 12))
        self.target = tk.Text(panel, height=4, wrap="word", bg=self.INPUT, fg=self.TEXT,
                              bd=0, padx=14, pady=14, font=("Segoe UI", 17))
        self.target.pack(fill="x", pady=(0, 12)); self.target.insert("1.0", self.lesson.text)
        self.target.configure(state="disabled")
        self.target.tag_configure("correct", foreground=self.GOOD)
        self.target.tag_configure("wrong", foreground=self.BAD, underline=True)
        self.target.tag_configure("current", background="#303949")
        self.entry = tk.Text(panel, height=4, wrap="word", bg=self.INPUT, fg=self.TEXT,
                             insertbackground=self.ACCENT, bd=0, padx=14, pady=14,
                             font=("Segoe UI", 17), undo=False)
        self.entry.pack(fill="x")
        self.entry.bind("<KeyPress>", self._key)
        self.entry.bind("<BackSpace>", self._backspace)
        tk.Label(panel, textvariable=self.status, bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=10)
        self._highlight(); self._show_keyboard(panel); self.entry.focus_set()

    def _key(self, event):
        if event.keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock", "Tab"):
            return
        char = event.char
        if not char or ord(char) < 32:
            return
        ok = self.session.add_char(char)
        self.entry.insert("end", char)
        if self.store.get_setting("speak_characters", True):
            self.speech.say(char if ok else "ошибка")
        self._highlight(); self._live()
        if self.session.finished:
            self._finish()
        return "break"

    def _backspace(self, event):
        if self.session.backspace() and self.entry.get("1.0", "end-1c"):
            self.entry.delete("end-2c", "end-1c")
        self._highlight(); self._live(); return "break"

    def _live(self):
        r = self.session.result()
        expected = self.session.expected or "готово"
        self.status.set(f"{r.elapsed:.1f} с • {r.wpm:.0f} WPM • {r.accuracy:.1f}% • ошибок: {r.errors} • следующая: {expected}")

    def _highlight(self):
        if not self.target: return
        self.target.configure(state="normal")
        for tag in ("correct", "wrong", "current"):
            self.target.tag_remove(tag, "1.0", "end")
        typed = self.session.typed; text = self.session.target
        for i, char in enumerate(typed):
            tag = "correct" if i < len(text) and char == text[i] else "wrong"
            self.target.tag_add(tag, f"1.{i}", f"1.{i+1}")
        if len(typed) < len(text):
            self.target.tag_add("current", f"1.{len(typed)}", f"1.{len(typed)+1}")
        self.target.configure(state="disabled")

    def _show_keyboard(self, parent):
        frame = tk.Frame(parent, bg=self.PANEL); frame.pack(fill="x", pady=(8, 0))
        expected = self.session.expected or ""
        for line in rows(self.language):
            row = tk.Frame(frame, bg=self.PANEL); row.pack()
            for char in line:
                bg = "#3b5f9e" if char.lower() == expected.lower() else "#252c38"
                tk.Label(row, text=char.upper(), width=4, pady=6, bg=bg, fg=self.TEXT,
                         font=("Segoe UI", 11, "bold")).pack(side="left", padx=2, pady=2)
        hint = finger_hint(self.language, expected) if expected else ""
        tk.Label(frame, text=hint, bg=self.PANEL, fg=self.MUTED).pack(pady=5)

    def _finish(self):
        r = self.session.result(); self.store.add_result(r, self.level, self.language)
        self.speech.say(f"Урок завершён. Точность {r.accuracy:.0f} процентов. Скорость {r.wpm:.0f} слов в минуту.")
        messagebox.showinfo("Урок завершён", f"Скорость: {r.wpm:.0f} WPM\nТочность: {r.accuracy:.1f}%\nОшибок: {r.errors}")

    def show_free(self):
        self._clear(); self._heading("Свободная печать", "Локальный текстовый редактор с озвучиванием")
        frame = tk.Frame(self.content, bg=self.PANEL, padx=22, pady=22); frame.pack(fill="both", expand=True, padx=32, pady=10)
        text = tk.Text(frame, bg=self.INPUT, fg=self.TEXT, insertbackground=self.TEXT,
                       bd=0, wrap="word", font=("Segoe UI", 16), padx=14, pady=14)
        text.pack(fill="both", expand=True); text.focus_set()
        def speak(_=None):
            value = text.get("1.0", "end-1c").strip()
            if value: self.speech.say(value)
            return "break"
        text.bind("<Control-space>", speak)
        self._button(frame, "🔊 Озвучить (Ctrl+Space)", speak).pack(anchor="w", pady=10)

    def show_stats(self):
        self._clear(); self._heading("Статистика", "История хранится локально")
        rows_data = self.store.sessions(); avg = averages(rows_data); errors = aggregate_key_errors(rows_data)
        top = tk.Frame(self.content, bg=self.BG); top.pack(fill="x", padx=32)
        tk.Label(top, text=f"Средний WPM: {avg['wpm']:.1f}   •   Точность: {avg['accuracy']:.1f}%   •   Ошибок: {avg['errors']:.1f}", bg=self.BG, fg=self.TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(top, text="Самые частые ошибочные клавиши: " + (", ".join(f"{k} ({v})" for k, v in list(errors.items())[:8]) or "нет данных"), bg=self.BG, fg=self.MUTED).pack(anchor="w", pady=8)
        tree = ttk.Treeview(self.content, columns=("lang", "level", "wpm", "acc", "err", "time"), show="headings")
        for col, title in (("lang", "Язык"), ("level", "Уровень"), ("wpm", "WPM"), ("acc", "Точность"), ("err", "Ошибки"), ("time", "Время")):
            tree.heading(col, text=title); tree.column(col, width=120, anchor="center")
        for row in reversed(rows_data):
            tree.insert("", "end", values=(row.get("language", "Русский"), row.get("level", ""), f"{float(row.get('wpm',0)):.0f}", f"{float(row.get('accuracy',0)):.1f}%", row.get("errors",0), f"{float(row.get('elapsed',0)):.1f} с"))
        tree.pack(fill="both", expand=True, padx=32, pady=12)

    def show_settings(self):
        self._clear(); self._heading("Настройки", "Параметры сохраняются локально")
        frame = tk.Frame(self.content, bg=self.PANEL, padx=24, pady=24); frame.pack(fill="x", padx=32)
        enabled = tk.BooleanVar(value=bool(self.store.get_setting("speech_enabled", True)))
        chars = tk.BooleanVar(value=bool(self.store.get_setting("speak_characters", True)))
        tk.Checkbutton(frame, text="Включить озвучивание", variable=enabled, bg=self.PANEL, fg=self.TEXT, selectcolor=self.INPUT, activebackground=self.PANEL, activeforeground=self.TEXT).pack(anchor="w", pady=4)
        tk.Checkbutton(frame, text="Озвучивать каждую клавишу", variable=chars, bg=self.PANEL, fg=self.TEXT, selectcolor=self.INPUT, activebackground=self.PANEL, activeforeground=self.TEXT).pack(anchor="w", pady=4)
        rate = tk.IntVar(value=int(self.store.get_setting("speech_rate", 175)))
        tk.Label(frame, text="Скорость речи", bg=self.PANEL, fg=self.MUTED).pack(anchor="w", pady=(15, 2))
        tk.Scale(frame, from_=80, to=260, variable=rate, orient="horizontal", length=420, bg=self.PANEL, fg=self.TEXT, highlightthickness=0).pack(anchor="w")
        def save():
            self.store.set_setting("speech_enabled", enabled.get()); self.store.set_setting("speak_characters", chars.get()); self.store.set_setting("speech_rate", rate.get())
            self.speech.enabled = enabled.get(); self.speech.rate = rate.get(); self.speech.restart()
            messagebox.showinfo("Настройки", "Настройки сохранены.")
        self._button(frame, "Сохранить", save).pack(anchor="w", pady=15)

    def close(self):
        self.speech.stop(); self.destroy()


def main():
    BlindTypingUI().mainloop()
