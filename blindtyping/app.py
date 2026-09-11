from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk, messagebox

from .engine import ENGLISH_TEXTS, LEVELS, RUSSIAN_TEXTS, TypingSession
from .speech import SpeechService
from .storage import HistoryStore


class BlindTypingApp(tk.Tk):
    BG = "#10131a"
    PANEL = "#191e28"
    TEXT = "#f2f4f8"
    MUTED = "#9aa4b2"
    ACCENT = "#6ea8fe"
    GOOD = "#72d6a5"
    BAD = "#ff7b7b"

    def __init__(self):
        super().__init__()
        self.title("BlindTyping — тренажёр слепой печати")
        self.geometry("1100x760")
        self.minsize(900, 650)
        self.configure(bg=self.BG)
        self.store = HistoryStore()
        self.speech = SpeechService(
            rate=int(self.store.get_setting("speech_rate", 175)),
            volume=float(self.store.get_setting("speech_volume", 1.0)),
        )
        self.level = "Начальный"
        self.language = "Русский"
        self.session = TypingSession(LEVELS[self.level][0])
        self.current_text = self.session.target
        self.nav_buttons: dict[str, tk.Button] = {}
        self.content: tk.Frame | None = None
        self.timer_job = None
        self._build_style()
        self._build_shell()
        self.show_dashboard()
        self.protocol("WM_DELETE_WINDOW", self.close)

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", background=self.PANEL, foreground=self.TEXT,
                        fieldbackground=self.PANEL, rowheight=32, borderwidth=0)
        style.configure("Treeview.Heading", background="#222936", foreground=self.TEXT,
                        relief="flat", font=("Segoe UI", 10, "bold"))
        style.configure("TCombobox", fieldbackground=self.PANEL, background=self.PANEL,
                        foreground=self.TEXT)

    def _build_shell(self):
        top = tk.Frame(self, bg=self.PANEL, height=64)
        top.pack(fill="x")
        tk.Label(top, text="⌨  BlindTyping", bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 21, "bold")).pack(side="left", padx=24, pady=14)
        tk.Label(top, text="офлайн • без ИИ • с озвучиванием", bg=self.PANEL,
                 fg=self.MUTED, font=("Segoe UI", 10)).pack(side="left", pady=18)

        nav = tk.Frame(self, bg="#141820", width=220)
        nav.pack(side="left", fill="y")
        for key, title in [
            ("home", "Главная"), ("train", "Тренировка"),
            ("free", "Свободная печать"), ("stats", "Статистика"),
            ("settings", "Настройки"),
        ]:
            b = tk.Button(nav, text=title, anchor="w", bd=0, padx=22, pady=14,
                          bg="#141820", fg=self.TEXT, activebackground="#242c39",
                          activeforeground=self.TEXT, font=("Segoe UI", 11),
                          command=lambda k=key: self.navigate(k))
            b.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[key] = b
        tk.Label(nav, text="\nЦель\nНе смотреть на клавиатуру\n\nТочность → скорость",
                 bg="#141820", fg=self.MUTED, justify="left", anchor="w",
                 font=("Segoe UI", 10)).pack(fill="x", padx=22, pady=20)
        self.content = tk.Frame(self, bg=self.BG)
        self.content.pack(side="left", fill="both", expand=True)

    def navigate(self, key: str):
        if key == "home": self.show_dashboard()
        elif key == "train": self.show_training()
        elif key == "free": self.show_free()
        elif key == "stats": self.show_stats()
        else: self.show_settings()

    def _clear(self):
        if self.content:
            for widget in self.content.winfo_children():
                widget.destroy()

    def _title(self, title: str, subtitle: str = ""):
        tk.Label(self.content, text=title, bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 25, "bold")).pack(anchor="w", padx=34, pady=(28, 4))
        if subtitle:
            tk.Label(self.content, text=subtitle, bg=self.BG, fg=self.MUTED,
                     font=("Segoe UI", 11)).pack(anchor="w", padx=36, pady=(0, 20))

    def _card(self, parent, title, value, hint=""):
        f = tk.Frame(parent, bg=self.PANEL, padx=20, pady=16)
        tk.Label(f, text=title, bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w")
        tk.Label(f, text=value, bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=4)
        if hint:
            tk.Label(f, text=hint, bg=self.PANEL, fg=self.MUTED,
                     font=("Segoe UI", 9)).pack(anchor="w")
        return f

    def show_dashboard(self):
        self._clear(); self._title("Добро пожаловать", "Тренажёр слепой печати с локальной статистикой и голосовой обратной связью")
        best = self.store.best()
        cards = tk.Frame(self.content, bg=self.BG); cards.pack(fill="x", padx=34)
        for title, value, hint in [
            ("Тренировок", str(best["sessions"]), "сохранено локально"),
            ("Лучший WPM", f"{best['wpm']:.0f}", "слов в минуту"),
            ("Лучшая точность", f"{best['accuracy']:.1f}%", "за завершённую тренировку"),
        ]:
            self._card(cards, title, value, hint).pack(side="left", fill="both", expand=True, padx=(0, 12))
        box = tk.Frame(self.content, bg=self.PANEL, padx=24, pady=22)
        box.pack(fill="x", padx=34, pady=24)
        tk.Label(box, text="Следующий шаг", bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(box, text="Начните с короткого упражнения. Программа подскажет ожидаемый символ и озвучит ошибки.",
                 bg=self.PANEL, fg=self.MUTED, wraplength=750, justify="left").pack(anchor="w", pady=8)
        self._button(box, "Начать тренировку", self.show_training).pack(anchor="w", pady=10)

    def _button(self, parent, text, command):
        return tk.Button(parent, text=text, command=command, bd=0, padx=18, pady=10,
                          bg="#2a6fdb", fg="white", activebackground="#3d82ed",
                          activeforeground="white", font=("Segoe UI", 10, "bold"), cursor="hand2")

    def show_training(self):
        self._clear(); self._title("Тренировка", "Выберите уровень и печатайте, не глядя на клавиатуру")
        controls = tk.Frame(self.content, bg=self.BG); controls.pack(fill="x", padx=34)
        tk.Label(controls, text="Уровень", bg=self.BG, fg=self.MUTED).pack(side="left")
        level_var = tk.StringVar(value=self.level)
        combo = ttk.Combobox(controls, textvariable=level_var, values=list(LEVELS), state="readonly", width=18)
        combo.pack(side="left", padx=10)
        combo.bind("<<ComboboxSelected>>", lambda e: self._new_training(level_var.get()))
        self._button(controls, "Новое задание", self._new_training).pack(side="left", padx=8)
        self._build_typing_area(training=True)

    def _new_training(self, level=None):
        self.level = level or self.level
        source = LEVELS[self.level]
        target = random.choice(source)
        self.session.reset(target)
        self.current_text = target
        self.show_training()

    def _build_typing_area(self, training=True):
        outer = tk.Frame(self.content, bg=self.PANEL, padx=22, pady=22)
        outer.pack(fill="both", expand=True, padx=34, pady=20)
        tk.Label(outer, text="Текст задания", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w")
        target = tk.Text(outer, height=5, wrap="word", bg="#11151c", fg=self.TEXT,
                         insertbackground=self.TEXT, bd=0, padx=16, pady=16,
                         font=("Segoe UI", 17))
        target.pack(fill="x", pady=(8, 16))
        target.insert("1.0", self.current_text)
        target.configure(state="disabled")
        target.tag_configure("correct", foreground=self.GOOD)
        target.tag_configure("wrong", foreground=self.BAD, underline=True)
        target.tag_configure("current", background="#303949")
        self.target_widget = target

        entry = tk.Text(outer, height=5, wrap="word", bg="#11151c", fg=self.TEXT,
                        insertbackground=self.ACCENT, bd=0, padx=16, pady=16,
                        font=("Segoe UI", 17), undo=False)
        entry.pack(fill="x")
        entry.bind("<KeyPress>", self._typing_key)
        entry.bind("<BackSpace>", self._backspace)
        self.entry = entry
        self.stats_label = tk.Label(outer, text="Готово • 0 CPM • 100%", bg=self.PANEL, fg=self.MUTED,
                                    font=("Segoe UI", 11))
        self.stats_label.pack(anchor="w", pady=12)
        self._highlight_current()
        entry.focus_set()

    def _typing_key(self, event):
        if event.keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock"):
            return
        char = event.char
        if not char or char == "\x08":
            return
        # We manage the text ourselves so the comparison is deterministic.
        self.entry.insert("end", char)
        ok = self.session.add_char(char)
        self.speech.say(char if ok else f"ошибка, нужно {self.current_text[len(self.session.typed)-1] if len(self.session.typed) <= len(self.current_text) else 'стоп'}")
        self._highlight_current()
        self._update_live_stats()
        if self.session.finished:
            self._finish_training()
        return "break"

    def _backspace(self, event):
        if self.session.finished:
            return "break"
        self.session.backspace()
        try: self.entry.delete("end-2c", "end-1c")
        except tk.TclError: pass
        self._highlight_current(); self._update_live_stats()
        return "break"

    def _highlight_current(self):
        if not hasattr(self, "target_widget"):
            return
        self.target_widget.configure(state="normal")
        self.target_widget.tag_remove("correct", "1.0", "end")
        self.target_widget.tag_remove("wrong", "1.0", "end")
        self.target_widget.tag_remove("current", "1.0", "end")
        typed = self.session.typed
        for i, char in enumerate(typed):
            tag = "correct" if i < len(self.current_text) and char == self.current_text[i] else "wrong"
            self.target_widget.tag_add(tag, f"1.{i}", f"1.{i+1}")
        if len(typed) < len(self.current_text):
            i = len(typed)
            self.target_widget.tag_add("current", f"1.{i}", f"1.{i+1}")
        self.target_widget.configure(state="disabled")

    def _update_live_stats(self):
        r = self.session.result()
        self.stats_label.configure(text=f"Время: {r.elapsed:.1f} с   •   {r.cpm:.0f} CPM   •   {r.wpm:.0f} WPM   •   Точность: {r.accuracy:.1f}%   •   Ошибок: {r.errors}")

    def _finish_training(self):
        r = self.session.result()
        self.store.add_result(r, self.level)
        self.speech.say(f"Тренировка завершена. Точность {r.accuracy:.0f} процентов. Скорость {r.wpm:.0f} слов в минуту.")
        messagebox.showinfo("Тренировка завершена", f"Скорость: {r.wpm:.0f} WPM\nТочность: {r.accuracy:.1f}%\nОшибок: {r.errors}")

    def show_free(self):
        self._clear(); self._title("Свободная печать", "Пишите любой текст. Ctrl+Space — озвучить введённое.")
        frame = tk.Frame(self.content, bg=self.PANEL, padx=24, pady=24)
        frame.pack(fill="both", expand=True, padx=34, pady=10)
        text = tk.Text(frame, bg="#11151c", fg=self.TEXT, insertbackground=self.TEXT,
                       bd=0, wrap="word", font=("Segoe UI", 16), padx=16, pady=16)
        text.pack(fill="both", expand=True)
        text.focus_set()
        def speak(_=None):
            value = text.get("1.0", "end-1c").strip()
            if value: self.speech.say(value)
        text.bind("<Control-space>", speak)
        self._button(frame, "🔊 Озвучить текст", speak).pack(anchor="w", pady=12)

    def show_stats(self):
        self._clear(); self._title("Статистика", "Последние результаты хранятся только на вашем компьютере")
        rows = self.store.sessions()
        tree = ttk.Treeview(self.content, columns=("level", "wpm", "acc", "errors", "time"), show="headings")
        for col, title in [("level", "Уровень"), ("wpm", "WPM"), ("acc", "Точность"), ("errors", "Ошибки"), ("time", "Время")]:
            tree.heading(col, text=title); tree.column(col, width=130, anchor="center")
        for row in reversed(rows):
            tree.insert("", "end", values=(row.get("level", ""), f"{row.get('wpm', 0):.0f}",
                                             f"{row.get('accuracy', 0):.1f}%", row.get("errors", 0),
                                             f"{row.get('elapsed', 0):.1f} с"))
        tree.pack(fill="both", expand=True, padx=34, pady=10)

    def show_settings(self):
        self._clear(); self._title("Настройки", "Параметры озвучивания и поведения тренажёра")
        frame = tk.Frame(self.content, bg=self.PANEL, padx=24, pady=24)
        frame.pack(fill="x", padx=34, pady=10)
        rate = tk.IntVar(value=int(self.store.get_setting("speech_rate", 175)))
        volume = tk.DoubleVar(value=float(self.store.get_setting("speech_volume", 1.0)))
        tk.Label(frame, text="Скорость речи", bg=self.PANEL, fg=self.TEXT).pack(anchor="w")
        tk.Scale(frame, from_=80, to=260, variable=rate, orient="horizontal", bg=self.PANEL,
                 fg=self.TEXT, highlightthickness=0, troughcolor="#303846").pack(fill="x", pady=(0, 18))
        tk.Label(frame, text="Громкость", bg=self.PANEL, fg=self.TEXT).pack(anchor="w")
        tk.Scale(frame, from_=0.1, to=1.0, resolution=0.1, variable=volume, orient="horizontal",
                 bg=self.PANEL, fg=self.TEXT, highlightthickness=0, troughcolor="#303846").pack(fill="x")
        def save():
            self.store.set_setting("speech_rate", rate.get())
            self.store.set_setting("speech_volume", volume.get())
            self.speech.rate, self.speech.volume = rate.get(), volume.get()
            messagebox.showinfo("Настройки", "Настройки сохранены")
        self._button(frame, "Сохранить", save).pack(anchor="w", pady=18)

    def close(self):
        if self.timer_job:
            self.after_cancel(self.timer_job)
        self.speech.stop()
        self.destroy()


def main():
    app = BlindTypingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
