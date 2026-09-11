from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .accessibility import AccessibilityController
from .analytics import aggregate_key_errors, averages
from .content import Lesson, random_lesson
from .engine import TypingSession
from .keyboard_layout import finger_hint, rows
from .speech import SpeechService
from .storage import HistoryStore


class BlindTypingUI(tk.Tk):
    """Accessible presentation layer. Core logic remains in independent modules."""

    BG = "#10131a"
    PANEL = "#191e28"
    INPUT = "#11151c"
    TEXT = "#f2f4f8"
    MUTED = "#b7c0cc"
    ACCENT = "#6ea8fe"
    GOOD = "#72d6a5"
    BAD = "#ff7b7b"

    def __init__(self):
        super().__init__()
        self.title("BlindTyping — тренажёр слепой печати")
        self.geometry("1180x820")
        self.minsize(900, 650)
        self.configure(bg=self.BG)
        self.store = HistoryStore()
        self.speech = SpeechService(
            rate=int(self.store.get_setting("speech_rate", 175)),
            volume=float(self.store.get_setting("speech_volume", 1.0)),
        )
        self.access = AccessibilityController(self.speech, self.store)
        self.language = str(self.store.get_setting("language", "Русский"))
        self.level = str(self.store.get_setting("level", "Начальный"))
        self.lesson: Lesson | None = None
        self.session: TypingSession | None = None
        self.entry: tk.Text | None = None
        self.target: tk.Text | None = None
        self.status = tk.StringVar(value="Готово")
        self.speech_status = tk.StringVar()
        self._current_page = "home"
        self._result_saved = False
        self._style()
        self._shell()
        self.bind_all("<F1>", self._help)
        self.bind_all("<F2>", self._toggle_speech)
        self.bind_all("<F3>", self._repeat_context)
        self.show_home()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(150, self._announce_home)

    def _style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", background=self.PANEL, foreground=self.TEXT,
                        fieldbackground=self.PANEL, rowheight=32)
        style.configure("Treeview.Heading", background="#252c38", foreground=self.TEXT,
                        relief="flat", font=("Segoe UI", 10, "bold"))
        style.configure("TCombobox", font=("Segoe UI", 11), padding=5)

    def _shell(self):
        header = tk.Frame(self, bg=self.PANEL)
        header.pack(fill="x")
        tk.Label(header, text="⌨ BlindTyping", bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 21, "bold")).pack(side="left", padx=22, pady=13)
        tk.Label(header, text="офлайн • без ИИ • доступность прежде всего",
                 bg=self.PANEL, fg=self.MUTED).pack(side="left")
        self.speech_button = tk.Button(
            header, textvariable=self.speech_status, command=self._toggle_speech,
            takefocus=True, bd=0, padx=16, pady=9, bg="#2a6fdb", fg="white",
            activebackground="#3d82ed", activeforeground="white",
            font=("Segoe UI", 10, "bold"), cursor="hand2",
        )
        self.speech_button.pack(side="right", padx=12, pady=10)
        self._update_speech_button()
        nav = tk.Frame(self, bg="#141820", width=220)
        nav.pack(side="left", fill="y")
        for key, title in (("home", "Главная"), ("train", "Уроки и тренировка"),
                           ("free", "Свободная печать"), ("stats", "Статистика"),
                           ("settings", "Настройки")):
            button = tk.Button(nav, text=title, anchor="w", takefocus=True, bd=0,
                               padx=20, pady=13, bg="#141820", fg=self.TEXT,
                               activebackground="#252d3a", activeforeground=self.TEXT,
                               font=("Segoe UI", 11), command=lambda k=key: self.navigate(k))
            button.pack(fill="x", padx=10, pady=3)
        help_button = tk.Button(nav, text="Помощь (F1)", anchor="w", takefocus=True,
                                bd=0, padx=20, pady=13, bg="#141820", fg=self.TEXT,
                                activebackground="#252d3a", activeforeground=self.TEXT,
                                font=("Segoe UI", 11), command=self._help)
        help_button.pack(fill="x", padx=10, pady=3)
        tk.Label(nav, text="\nF2 — озвучка\nF3 — повторить подсказку\nTab — следующий элемент\nShift+Tab — предыдущий\n\nТочность → ритм → скорость",
                 bg="#141820", fg=self.MUTED, justify="left", anchor="w",
                 font=("Segoe UI", 9)).pack(fill="x", padx=20, pady=18)
        self.content = tk.Frame(self, bg=self.BG)
        self.content.pack(side="left", fill="both", expand=True)

    def _update_speech_button(self):
        state = "ВКЛ" if self.access.enabled else "ВЫКЛ"
        self.speech_status.set(f"🔊 Озвучка: {state} (F2)")

    def _toggle_speech(self, _event=None):
        self.access.toggle()
        self._update_speech_button()
        return "break"

    def _repeat_context(self, _event=None):
        if self._current_page == "train" and self.lesson and self.session:
            expected = self.session.expected
            hint = finger_hint(self.language, expected) if expected else "задание завершено"
            self.access.speak(f"Урок: {self.lesson.title}. Следующая клавиша: {self.access.describe_char(expected) or 'нет'}. {hint}")
        elif self._current_page == "free":
            self.access.speak("Свободная печать. Напишите текст и нажмите Ctrl+пробел для озвучивания.")
        else:
            self.access.speak("Главное меню. F2 включает и выключает озвучку. F1 открывает помощь.")
        return "break"

    def _help(self, _event=None):
        self.access.speak("Управление. F2 — включить или выключить озвучку. F3 — повторить текущую подсказку. Tab — перейти к следующему элементу. Shift плюс Tab — к предыдущему. Enter или пробел — активировать кнопку. В тренировке программа озвучивает ошибки. В настройках можно включить озвучивание каждой клавиши. В свободной печати Ctrl плюс пробел озвучивает введённый текст.")
        return "break"

    def _announce_home(self):
        self.access.speak("Главная. Нажмите Tab для перехода по элементам. F2 — озвучка. F1 — помощь.")

    def navigate(self, page: str):
        self._current_page = page
        {"home": self.show_home, "train": self.show_train, "free": self.show_free,
         "stats": self.show_stats, "settings": self.show_settings}[page]()

    def _clear(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        self.entry = None
        self.target = None

    def _heading(self, title: str, subtitle: str = ""):
        tk.Label(self.content, text=title, bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 25, "bold")).pack(anchor="w", padx=32, pady=(26, 4))
        if subtitle:
            tk.Label(self.content, text=subtitle, bg=self.BG, fg=self.MUTED,
                     font=("Segoe UI", 11), wraplength=820, justify="left").pack(anchor="w", padx=34, pady=(0, 18))

    def _button(self, parent, text, command):
        return tk.Button(parent, text=text, command=command, takefocus=True, bd=0,
                         padx=17, pady=10, bg="#2a6fdb", fg="white",
                         activebackground="#3d82ed", activeforeground="white",
                         font=("Segoe UI", 10, "bold"), cursor="hand2")

    def show_home(self):
        self._clear(); self._heading("Главная", "Тренажёр слепой печати с управлением с клавиатуры и голосовой обратной связью.")
        best = self.store.best(); avg = averages(self.store.sessions())
        cards = tk.Frame(self.content, bg=self.BG); cards.pack(fill="x", padx=32)
        for title, value in (("Тренировок", str(int(best["sessions"]))), ("Лучший WPM", f"{best['wpm']:.0f}"), ("Средний WPM", f"{avg['wpm']:.0f}"), ("Средняя точность", f"{avg['accuracy']:.1f}%")):
            box = tk.Frame(cards, bg=self.PANEL, padx=18, pady=16)
            box.pack(side="left", fill="both", expand=True, padx=(0, 10))
            tk.Label(box, text=title, bg=self.PANEL, fg=self.MUTED).pack(anchor="w")
            tk.Label(box, text=value, bg=self.PANEL, fg=self.TEXT, font=("Segoe UI", 21, "bold")).pack(anchor="w", pady=4)
        box = tk.Frame(self.content, bg=self.PANEL, padx=24, pady=24); box.pack(fill="x", padx=32, pady=24)
        tk.Label(box, text="Начать обучение", bg=self.PANEL, fg=self.TEXT, font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(box, text="F2 — озвучка. F3 — повторить подсказку. F1 — помощь. Tab и Enter позволяют работать без мыши.", bg=self.PANEL, fg=self.MUTED, wraplength=800, justify="left").pack(anchor="w", pady=8)
        self._button(box, "Начать урок", self.show_train).pack(anchor="w", pady=8)

    def show_train(self):
        self._clear(); self._heading("Уроки и тренировка", "Выберите язык и уровень. Поле ввода получает фокус автоматически.")
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
        self.store.set_setting("language", self.language); self.store.set_setting("level", self.level)
        self.lesson = random_lesson(self.language, self.level); self.session = TypingSession(self.lesson.text); self._result_saved = False
        self.show_train()

    def _build_lesson(self):
        if self.lesson is None:
            self.lesson = random_lesson(self.language, self.level); self.session = TypingSession(self.lesson.text); self._result_saved = False
        panel = tk.Frame(self.content, bg=self.PANEL, padx=22, pady=20); panel.pack(fill="both", expand=True, padx=32, pady=20)
        tk.Label(panel, text=self.lesson.title, bg=self.PANEL, fg=self.TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(panel, text=self.lesson.hint, bg=self.PANEL, fg=self.MUTED, wraplength=850, justify="left").pack(anchor="w", pady=(2, 12))
        self.target = tk.Text(panel, height=4, wrap="word", bg=self.INPUT, fg=self.TEXT, bd=0, padx=14, pady=14, font=("Segoe UI", 17), takefocus=False)
        self.target.pack(fill="x", pady=(0, 12)); self.target.insert("1.0", self.lesson.text); self.target.configure(state="disabled")
        self.target.tag_configure("correct", foreground=self.GOOD); self.target.tag_configure("wrong", foreground=self.BAD, underline=True); self.target.tag_configure("current", background="#303949")
        self.entry = tk.Text(panel, height=4, wrap="word", bg=self.INPUT, fg=self.TEXT, insertbackground=self.ACCENT, bd=0, padx=14, pady=14, font=("Segoe UI", 17), undo=False, takefocus=True)
        self.entry.pack(fill="x"); self.entry.bind("<KeyPress>", self._key); self.entry.bind("<BackSpace>", self._backspace); self.entry.bind("<Tab>", self._focus_next); self.entry.bind("<Shift-Tab>", self._focus_previous)
        tk.Label(panel, textvariable=self.status, bg=self.PANEL, fg=self.MUTED, font=("Segoe UI", 10), wraplength=850, justify="left").pack(anchor="w", pady=10)
        self._highlight(); self._show_keyboard(panel); self.entry.focus_set()
        self.after(100, lambda: self.access.speak(f"{self.lesson.title}. {self.lesson.hint}. Следующая клавиша: {self.access.describe_char(self.session.expected)}."))

    def _focus_next(self, _event=None):
        if self.entry:
            next_widget = self.entry.tk.call("tk_focusNext", self.entry._w)
            if next_widget:
                self.nametowidget(next_widget).focus_set()
        return "break"

    def _focus_previous(self, _event=None):
        if self.entry:
            previous_widget = self.entry.tk.call("tk_focusPrev", self.entry._w)
            if previous_widget:
                self.nametowidget(previous_widget).focus_set()
        return "break"

    def _key(self, event):
        if not self.session or self.session.finished:
            return "break"
        if event.keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock", "Tab", "F1", "F2", "F3"):
            return
        char = event.char
        if not char or ord(char) < 32:
            return
        expected = self.session.expected; ok = self.session.add_char(char); self.entry.insert("end", char)
        self.access.character_feedback(char, ok, expected); self._highlight(); self._live()
        if self.session.finished: self._finish()
        return "break"

    def _backspace(self, event):
        if self.session and not self.session.finished and self.session.backspace():
            if self.entry and self.entry.get("1.0", "end-1c"): self.entry.delete("end-2c", "end-1c")
            self._highlight(); self._live()
        return "break"

    def _live(self):
        r = self.session.result(); expected = self.session.expected or "готово"; hint = finger_hint(self.language, self.session.expected) if self.session.expected else ""
        self.status.set(f"{r.elapsed:.1f} с • {r.wpm:.0f} WPM • {r.accuracy:.1f}% • ошибок: {r.errors} • следующая: {self.access.describe_char(expected)} • {hint}")

    def _highlight(self):
        if not self.target or not self.session: return
        self.target.configure(state="normal")
        for tag in ("correct", "wrong", "current"): self.target.tag_remove(tag, "1.0", "end")
        typed = self.session.typed; text = self.session.target
        for i, char in enumerate(typed):
            self.target.tag_add("correct" if i < len(text) and char == text[i] else "wrong", f"1.{i}", f"1.{i+1}")
        if len(typed) < len(text): self.target.tag_add("current", f"1.{len(typed)}", f"1.{len(typed)+1}")
        self.target.configure(state="disabled")

    def _show_keyboard(self, parent):
        frame = tk.Frame(parent, bg=self.PANEL); frame.pack(fill="x", pady=(8, 0)); expected = self.session.expected or ""
        for line in rows(self.language):
            row = tk.Frame(frame, bg=self.PANEL); row.pack()
            for char in line:
                bg = "#3b5f9e" if char.lower() == expected.lower() else "#252c38"
                tk.Label(row, text=char.upper(), width=4, pady=6, bg=bg, fg=self.TEXT, font=("Segoe UI", 11, "bold")).pack(side="left", padx=2, pady=2)
        tk.Label(frame, text=finger_hint(self.language, expected) if expected else "", bg=self.PANEL, fg=self.MUTED).pack(pady=5)

    def _finish(self):
        if self._result_saved: return
        self._result_saved = True; r = self.session.result(); self.store.add_result(r, self.level, self.language)
        self.access.speak(f"Урок завершён. Точность {r.accuracy:.0f} процентов. Скорость {r.wpm:.0f} слов в минуту. Ошибок: {r.errors}.")
        self.status.set(f"Завершено. {r.wpm:.0f} WPM • {r.accuracy:.1f}% • ошибок: {r.errors}.")
        if self.entry: self.entry.configure(state="disabled")
        button = self._button(self.content, "Новое упражнение", lambda: self._start_lesson()); button.pack(anchor="w", padx=32, pady=(0, 12)); button.focus_set()

    def show_free(self):
        self._clear(); self._heading("Свободная печать", "Локальный текстовый редактор. Ctrl+пробел озвучивает весь введённый текст.")
        frame = tk.Frame(self.content, bg=self.PANEL, padx=22, pady=22); frame.pack(fill="both", expand=True, padx=32, pady=10)
        text = tk.Text(frame, bg=self.INPUT, fg=self.TEXT, insertbackground=self.TEXT, bd=0, wrap="word", font=("Segoe UI", 16), padx=14, pady=14, takefocus=True)
        text.pack(fill="both", expand=True); text.focus_set()
        def speak(_=None):
            self.access.speak(text.get("1.0", "end-1c").strip() or "Текст пустой"); return "break"
        text.bind("<Control-space>", speak)
        text.bind("<Tab>", lambda _e: self._focus_free_next(text))
        self._button(frame, "🔊 Озвучить текст (Ctrl+пробел)", speak).pack(anchor="w", pady=10)

    def _focus_free_next(self, widget):
        next_widget = widget.tk.call("tk_focusNext", widget._w)
        if next_widget: self.nametowidget(next_widget).focus_set()
        return "break"

    def show_stats(self):
        self._clear(); self._heading("Статистика", "Результаты хранятся только локально на этом компьютере.")
        rows_data = self.store.sessions(); avg = averages(rows_data); errors = aggregate_key_errors(rows_data)
        tk.Label(self.content, text=f"Средний WPM: {avg['wpm']:.1f} • Точность: {avg['accuracy']:.1f}% • Ошибок: {avg['errors']:.1f}", bg=self.BG, fg=self.TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=32)
        tk.Label(self.content, text="Чаще всего ошибались на: " + (", ".join(f"{k} ({v})" for k, v in list(errors.items())[:8]) or "нет данных"), bg=self.BG, fg=self.MUTED, wraplength=850, justify="left").pack(anchor="w", padx=32, pady=8)
        tree = ttk.Treeview(self.content, columns=("lang", "level", "wpm", "acc", "errors", "time"), show="headings", takefocus=True)
        for col, title in (("lang", "Язык"), ("level", "Уровень"), ("wpm", "WPM"), ("acc", "Точность"), ("errors", "Ошибки"), ("time", "Время")):
            tree.heading(col, text=title); tree.column(col, width=125, anchor="center")
        for row in reversed(rows_data):
            tree.insert("", "end", values=(row.get("language", "Русский"), row.get("level", ""), f"{float(row.get('wpm', 0)):.0f}", f"{float(row.get('accuracy', 0)):.1f}%", row.get("errors", 0), f"{float(row.get('elapsed', 0)):.1f} с"))
        tree.pack(fill="both", expand=True, padx=32, pady=10)

    def show_settings(self):
        self._clear(); self._heading("Настройки", "Параметры озвучивания и доступности.")
        frame = tk.Frame(self.content, bg=self.PANEL, padx=24, pady=24); frame.pack(fill="x", padx=32, pady=10)
        rate = tk.IntVar(value=int(self.store.get_setting("speech_rate", 175))); volume = tk.DoubleVar(value=float(self.store.get_setting("speech_volume", 1.0)))
        chars = tk.BooleanVar(value=self.access.speak_characters); errors = tk.BooleanVar(value=self.access.speak_errors); enabled = tk.BooleanVar(value=self.access.enabled)
        tk.Label(frame, text="Скорость речи", bg=self.PANEL, fg=self.TEXT).pack(anchor="w")
        tk.Scale(frame, from_=80, to=260, variable=rate, orient="horizontal", bg=self.PANEL, fg=self.TEXT, highlightthickness=0, troughcolor="#303846").pack(fill="x", pady=(0, 12))
        tk.Label(frame, text="Громкость", bg=self.PANEL, fg=self.TEXT).pack(anchor="w")
        tk.Scale(frame, from_=0.1, to=1.0, resolution=0.1, variable=volume, orient="horizontal", bg=self.PANEL, fg=self.TEXT, highlightthickness=0, troughcolor="#303846").pack(fill="x")
        tk.Checkbutton(frame, text="Озвучивать каждую правильную клавишу", variable=chars, bg=self.PANEL, fg=self.TEXT, selectcolor=self.INPUT, activebackground=self.PANEL, activeforeground=self.TEXT).pack(anchor="w", pady=(14, 4))
        tk.Checkbutton(frame, text="Озвучивать ошибки", variable=errors, bg=self.PANEL, fg=self.TEXT, selectcolor=self.INPUT, activebackground=self.PANEL, activeforeground=self.TEXT).pack(anchor="w", pady=4)
        tk.Checkbutton(frame, text="Включить озвучку", variable=enabled, bg=self.PANEL, fg=self.TEXT, selectcolor=self.INPUT, activebackground=self.PANEL, activeforeground=self.TEXT).pack(anchor="w", pady=4)
        def save():
            self.access.speak_characters = chars.get(); self.access.speak_errors = errors.get(); self.access.enabled = enabled.get()
            self.speech.set_rate(rate.get()); self.speech.set_volume(volume.get()); self.speech.set_enabled(enabled.get())
            self.store.set_setting("speech_rate", rate.get()); self.store.set_setting("speech_volume", volume.get()); self.access.save_preferences(); self._update_speech_button()
            if self.access.enabled: self.access.speak("Настройки сохранены")
        self._button(frame, "Сохранить настройки", save).pack(anchor="w", pady=18)

    def close(self):
        self.speech.stop(); self.destroy()


def main():
    app = BlindTypingUI(); app.mainloop()


if __name__ == "__main__":
    main()
