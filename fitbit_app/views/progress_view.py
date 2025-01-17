import tkinter as tk
from tkinter import ttk

class ProgressView(tk.Toplevel):
    def __init__(self, master, message):
        super().__init__(master)
        self.message = message

        self.title("進捗状況")

        # ウィンドウの大きさを指定
        window_width = 250
        window_height = 100

        # ウィンドウを画面中央に配置
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        pos_x = (screen_width // 2) - (window_width // 2)
        pos_y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

        # 閉じるボタンを無効化
        self.protocol("WM_DELETE_WINDOW", self.disable_close_button)

        self.date_label = ttk.Label(self, text=message, font=("normal", 11))
        self.date_label.pack(pady=30)

    def close(self):
        self.destroy()

    def disable_close_button(self):
        pass
