import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
from keyboard import VirtualKeyboard

class BlindTypingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BlindTyping")
        self.root.geometry("900x600")
        self.root.configure(bg="#f8f9fa")
        
        # --- Верхнее меню ---
        menu_frame = tk.Frame(root, bg="#f8f9fa")
        menu_frame.pack(fill="x", pady=5)
        menu_items = ["Главная", "Тест", "Тексты", "Практика", "Клавиатура", "Поддержка"]
        for item in menu_items:
            btn = tk.Label(menu_frame, text=item, bg="#f8f9fa", fg="#000",
                           font=("Arial", 10), cursor="hand2")
            btn.pack(side="right", padx=10)
            btn.bind("<Button-1>", lambda e, name=item: self.menu_clicked(name))

        # --- Заголовок ---
        title = tk.Label(root, text="Клавиатурный Тренажёр", font=("Arial", 14, "bold"),
                         bg="#f8f9fa", anchor="w")
        title.pack(fill="x", padx=20, pady=(10, 5))

        # --- Эталонный текст (только для чтения) ---
        self.text_reference_display = tk.Text(root, wrap="word", height=8, font=("Consolas", 14),
                                              bg="#ffffff", relief="solid", bd=1)
        self.text_reference_display.pack(fill="both", expand=True, padx=20, pady=5)
        self.text_reference_display.configure(state="disabled")

        # --- Поле для ввода ---
        self.text_input = tk.Text(root, wrap="word", height=8, font=("Consolas", 14),
                                  bg="#f0f0f0", relief="solid", bd=1)
        self.text_input.pack(fill="both", expand=True, padx=20, pady=5)

        # --- Нижняя панель ---
        bottom_frame = tk.Frame(root, bg="#f8f9fa")
        bottom_frame.pack(fill="x", pady=10)

        self.stats = tk.Label(bottom_frame,
                              text="WPM: 0    CPM: 0    Точность: 100%    Ошибок: 0 ",
                              bg="#f8f9fa", fg="#000", font=("Arial", 10))
        self.stats.pack(side="left", padx=20)

        self.btn_start = ttk.Button(bottom_frame, text="Start ", command=self.start_typing)
        self.btn_reset = ttk.Button(bottom_frame, text="Reset ", command=self.reset_test)
        self.btn_start.pack(side="left", padx=5)
        self.btn_reset.pack(side="left", padx=5)

        # --- Виртуальная клавиатура (СВЯЗЬ) ---
        # Передаём root, поле ввода и функцию обратного вызова
        self.vkb = VirtualKeyboard(root, target_input=self.text_input, stats_callback=self.on_key_press)

        # --- Подвал ---
        footer = tk.Label(root, text="© 2024 BlindTyping. Поддержка | FAQ ",
                          bg="#f8f9fa", fg="#6c757d", font=("Arial", 9))
        footer.pack(side="bottom", pady=5)

        # --- Логика ---
        self.text_reference = ""
        self.start_time = None
        self.running = False
        self.errors = 0
        self.correct_chars = 0
        self.update_job = None

    def generate_text(self):
        samples = [
            "Сегодня отличный день, чтобы научиться печатать быстрее. ",
            "Не спешите, главное — точность и уверенность при наборе текста. ",
            "Учиться печатать вслепую — значит доверять памяти своих пальцев. ",
            "Практика делает мастера, особенно когда вы внимательны к деталям. "
        ]
        return random.choice(samples)

    def menu_clicked(self, name):
        messagebox.showinfo("Меню", f"Вы нажали: {name}")

    def start_typing(self):
        if not self.running:
            self.running = True
            self.text_reference = self.generate_text()
            self.errors = 0
            self.correct_chars = 0

            # --- Отображение эталонного текста ---
            self.text_reference_display.configure(state="normal")
            self.text_reference_display.delete("1.0", "end")
            self.text_reference_display.insert("1.0", self.text_reference)
            self.text_reference_display.configure(state="disabled")

            # --- Поле ввода ---
            self.text_input.configure(state="normal")
            self.text_input.delete("1.0", "end")
            self.text_input.focus_set()
            self.text_input.bind("<KeyRelease>", self.on_key_release)

            self.start_time = time.time()
            self.update_stats()
            self.btn_start.configure(state="disabled")

    def reset_test(self):
        self.running = False
        if self.update_job:
            self.root.after_cancel(self.update_job)
        self.errors = 0
        self.correct_chars = 0
        self.start_time = None
        self.stats.configure(text="WPM: 0    CPM: 0    Точность: 100%    Ошибок: 0 ")

        self.text_input.configure(state="normal")
        self.text_input.delete("1.0", "end")

        self.btn_start.configure(state="normal")

    def on_key_press(self, char):
        """Вызывается клавиатурой при нажатии для обновления статистики"""
        # Эта функция может использоваться для подсчёта нажатий в реальном времени
        pass

    def on_key_release(self, event):
        typed_text = self.text_input.get("1.0", "end-1c")

        # --- Настройка цветов тегов ---
        self.text_input.tag_config("correct", foreground="green")
        self.text_input.tag_config("wrong", foreground="red")

        self.errors = 0
        self.correct_chars = 0

        # Сбрасываем предыдущие подсветки
        self.text_input.tag_remove("correct", "1.0", "end")
        self.text_input.tag_remove("wrong", "1.0", "end")

        # Подсветка только введённого текста
        for i in range(len(typed_text)):
            if i < len(self.text_reference):
                if typed_text[i] == self.text_reference[i]:
                    self.text_input.tag_add("correct", f"1.{i}", f"1.{i+1}")
                    self.correct_chars += 1
                else:
                    self.text_input.tag_add("wrong", f"1.{i}", f"1.{i+1}")
                    self.errors += 1

    def update_stats(self):
        if self.running:
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                cpm = int((self.correct_chars / elapsed) * 60)
                wpm = int(cpm / 5)
                total = max(1, len(self.text_reference))
                accuracy = int((self.correct_chars / total) * 100)
                self.stats.configure(
                    text=f"WPM: {wpm}    CPM: {cpm}    Точность: {accuracy}%    Ошибок: {self.errors}"
                )
            self.update_job = self.root.after(500, self.update_stats)

if __name__ == "__main__":
    root = tk.Tk()
    app = BlindTypingApp(root)
    root.mainloop()