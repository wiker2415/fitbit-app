import tkinter as tk
from tkinter import ttk

class ProgressbarView(tk.Toplevel):
    def __init__(self, master, total_count):
        super().__init__(master)
        self.total_count = total_count

        self.title("進捗状況")

        # ウィンドウの大きさを指定
        window_width = 300
        window_height = 140

        # ウィンドウを画面中央に配置
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        pos_x = (screen_width // 2) - (window_width // 2)
        pos_y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

        self.progressbar = ttk.Progressbar(self, length=250, maximum=self.total_count, mode="determinate")
        self.progressbar.pack(pady=(40, 20))

        self.date_label = ttk.Label(self, text="準備中...")
        self.date_label.pack(pady=10)

    def update_progress(self, current: int, date):
        """外部から進捗を更新するメソッド

        Args:
            current (int): 現在の進捗(0から始まる)
            total (int): 全体の要素数
            date (datetime.date): 取得するデータの日付
        """
        self.date_label.config(text=f'{date}のデータを取得しています。')
        self.progressbar["value"] = current
        self.update_idletasks()

        if current == self.total_count:
            self.destroy()


