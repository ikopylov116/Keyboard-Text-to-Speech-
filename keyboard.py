import tkinter as tk
from pynput import keyboard
import threading
import pyttsx3

class VirtualKeyboard:
    def __init__(self, root, target_input=None):
        self.root = root
        self.target_input = target_input
        self.caps_lock = False
        self.shift_active = False
        self.keys = {}
        self.listener = None
        self.is_running = True
        
        # Индикатор Caps Lock
        self.caps_label = tk.Label(root, text="caps ", font=('Arial', 10),
                                  bg='#1a1a2e', fg='#4a4a6a')
        self.caps_label.pack(anchor='e', padx=20, pady=(5, 0))
        
        self.layout = [
            ['Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З', 'Х', 'Ъ'],
            ['Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д', 'Ж', 'Э'],
            ['Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь', 'Б', 'Ю', ','],
        ]
        
        self.create_keyboard()
        self.start_listener()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def safe_ui_call(self, func, *args, **kwargs):
        if self.is_running and self.root.winfo_exists():
            self.root.after(0, func, *args, **kwargs)

    def create_btn(self, parent, text, width, cmd=None):
        btn = tk.Button(parent, text=text, width=width, font=('Arial', 14),
                       bg='#2a2a3e', fg='#c0c0c0', relief='flat',
                       highlightthickness=1, highlightbackground='#4a4a6a',
                       activebackground='#4a4a7e', activeforeground='white',
                       cursor='hand2')
        btn.pack(side=tk.LEFT, padx=3, ipady=12)
        if cmd:
            btn.bind('<Button-1>', cmd)
        btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#353555', highlightbackground='#5a5a8a'))
        btn.bind('<Leave>', lambda e, b=btn: b.configure(bg='#2a2a3e', highlightbackground='#4a4a6a'))
        return btn

    def create_keyboard(self):
        kb_frame = tk.Frame(self.root, bg='#1a1a2e')
        kb_frame.pack(pady=20, fill=tk.X)
        
        for row in self.layout:
            row_frame = tk.Frame(kb_frame, bg='#1a1a2e')
            row_frame.pack(pady=2)
            for key in row:
                btn = self.create_btn(row_frame, key, 5)
                self.keys[key.lower()] = btn
        
        row_frame = tk.Frame(kb_frame, bg='#1a1a2e')
        row_frame.pack(pady=2)
        
        self.keys['caps'] = self.create_btn(row_frame, '🔒 Caps', 10, lambda e: self.toggle_caps())
        self.keys['shift'] = self.create_btn(row_frame, '⇧ Shift', 10, lambda e: self.toggle_shift())
        self.keys['space'] = self.create_btn(row_frame, '␣', 30, lambda e: self.insert_char(' '))
        self.keys['backspace'] = self.create_btn(row_frame, '⌫', 8, lambda e: self.delete_char())
        self.keys['speak'] = self.create_btn(row_frame, '🔊 Speak', 10, lambda e: self.speak_text())

    def toggle_caps(self):
        self.caps_lock = not self.caps_lock
        self.caps_label.configure(fg='#4a6a4a' if self.caps_lock else '#4a4a6a',
                                 text='CAPS' if self.caps_lock else 'caps')
        self.update_letters()

    def toggle_shift(self):
        self.shift_active = not self.shift_active
        self.update_letters()

    def update_letters(self):
        for key, btn in self.keys.items():
            if len(key) == 1 and key.isalpha():
                new_text = key.upper() if self.caps_lock or self.shift_active else key.lower()
                btn.configure(text=new_text)

    def highlight(self, key_name, pressed):
        if key_name in self.keys and key_name not in ['caps', 'shift', 'speak']:
            btn = self.keys[key_name]
            if btn.winfo_exists():
                color = '#4a4a7e' if pressed else '#2a2a3e'
                btn.configure(bg=color, fg='white' if pressed else '#c0c0c0')

    def on_press(self, key):
        try:
            # Ctrl для озвучивания всего текста
            if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.safe_ui_call(self.speak_text)
                return
            
            if hasattr(key, 'char') and key.char:
                char = key.char
                self.safe_ui_call(self.highlight, char.lower(), True)
                self.safe_ui_call(self.insert_char, char)
                # Озвучиваем КАЖДУЮ букву сразу
                self.safe_ui_call(self.speak_char, char)
            
            if key == keyboard.Key.space:
                self.safe_ui_call(self.highlight, 'space', True)
                self.safe_ui_call(self.insert_char, ' ')
                self.safe_ui_call(self.speak_char, ' ')
            elif key == keyboard.Key.backspace:
                self.safe_ui_call(self.highlight, 'backspace', True)
                self.safe_ui_call(self.delete_char)
                self.safe_ui_call(self.speak_char, 'удалить')
            elif key == keyboard.Key.caps_lock:
                self.safe_ui_call(self.toggle_caps)
            elif key == keyboard.Key.shift:
                self.shift_active = True
                self.safe_ui_call(self.update_letters)
        except Exception as e:
            print(f"Press error: {e}")

    def on_release(self, key):
        try:
            if hasattr(key, 'char') and key.char:
                self.safe_ui_call(self.highlight, key.char.lower(), False)
            
            if key == keyboard.Key.space:
                self.safe_ui_call(self.highlight, 'space', False)
            elif key == keyboard.Key.backspace:
                self.safe_ui_call(self.highlight, 'backspace', False)
            elif key == keyboard.Key.shift:
                self.shift_active = False
                self.safe_ui_call(self.update_letters)
        except Exception as e:
            print(f"Release error: {e}")

    def insert_char(self, char):
        if self.target_input and self.target_input.winfo_exists():
            try:
                self.target_input.insert(tk.END, char)
                self.target_input.see(tk.END)
            except Exception as e:
                print(f"Insert error: {e}")

    def delete_char(self):
        if self.target_input and self.target_input.winfo_exists():
            try:
                self.target_input.delete("end-2c", "end-1c")
            except Exception as e:
                print(f"Delete error: {e}")

    def get_current_text(self):
        if self.target_input and self.target_input.winfo_exists():
            try:
                return self.target_input.get("1.0", tk.END).strip()
            except:
                return ""
        return ""

    def speak_char(self, char):
        """Озвучивание ОДНОГО символа"""
        def speak_thread():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 200)  # Быстрее для отдельных букв
                engine.setProperty('volume', 0.8)
                voices = engine.getProperty('voices')
                for voice in voices:
                    if 'ru' in voice.id.lower():
                        engine.setProperty('voice', voice.id)
                        break
                engine.say(char)
                engine.runAndWait()
                engine.stop()
                del engine
            except Exception as e:
                pass  # Тихо игнорируем ошибки для отдельных букв
        
        threading.Thread(target=speak_thread, daemon=True).start()

    def speak_text(self):
        """Озвучивание ВСЕГО текста"""
        text = self.get_current_text()
        if not text:
            return
        
        def speak_thread():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 170)  # Нормальная скорость для текста
                engine.setProperty('volume', 1.0)
                voices = engine.getProperty('voices')
                for voice in voices:
                    if 'ru' in voice.id.lower():
                        engine.setProperty('voice', voice.id)
                        break
                engine.say(text)
                engine.runAndWait()
                engine.stop()
                del engine
            except Exception as e:
                print(f"Speech error: {e}")
        
        threading.Thread(target=speak_thread, daemon=True).start()

    def start_listener(self):
        def listener_thread():
            with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                self.listener = listener
                listener.join()
        threading.Thread(target=listener_thread, daemon=True).start()

    def on_close(self):
        self.is_running = False
        if self.listener:
            self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Виртуальная Клавиатура")
    root.configure(bg='#1a1a2e')
    root.geometry("800x400")
    
    text_area = tk.Text(root, height=6, font=('Arial', 18), bg='#2a2a3e', fg='white',
                       insertbackground='white')
    text_area.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
    
    hint = tk.Label(root, text="🔤 Каждая буква озвучивается | CTRL = озвучить весь текст", 
                   font=('Arial', 12), bg='#1a1a2e', fg='#6a6a8a')
    hint.pack(pady=5)
    
    kb = VirtualKeyboard(root, target_input=text_area)
    root.mainloop()