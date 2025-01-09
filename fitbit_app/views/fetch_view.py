import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
from ..controllers.view_controller import ViewController
from ..controllers.fetch_controller import FetchController

class FetchView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.master = master
        self.master.title("データ取得画面")

        # ウィンドウの大きさを指定
        window_width = 350
        window_height = 300

        # ウィンドウを画面中央に配置
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        pos_x = (screen_width // 2) - (window_width // 2)
        pos_y = (screen_height // 2) - (window_height // 2)
        self.master.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
        
        label = tk.Label(self.master, text="データ取得画面です。", wraplength=300)
        label.pack(pady=20)

        # 開始日入力フォーム
        self.start_date_frame = tk.Frame(self.master)
        self.start_date_frame.pack(anchor=tk.CENTER, pady=10)
        self.start_date_label = tk.Label(self.start_date_frame, text="開始日: ")
        self.start_date_label.pack(side=tk.LEFT, padx=5)
        self.start_date_entry = DateEntry(self.start_date_frame, showweeknumbers=False, date_pattern="yyyy/mm/dd", locale='ja_JP')
        self.start_date_entry.pack(side=tk.LEFT, padx=5)

        # 終了日入力フォーム
        self.end_date_frame = tk.Frame(self.master)
        self.end_date_frame.pack(anchor=tk.CENTER, pady=10)
        self.end_date_label = tk.Label(self.end_date_frame, text="終了日: ")
        self.end_date_label.pack(side=tk.LEFT, padx=5)
        self.end_date_entry = DateEntry(self.end_date_frame, showweeknumbers=False, date_pattern="yyyy/mm/dd", locale='ja_JP')
        self.end_date_entry.pack(side=tk.LEFT, padx=5)

        self.fetch_button = tk.Button(self.master, text="データを取得する", command=self.fetch_data)
        self.fetch_button.pack(pady=20)

        self.close_button = tk.Button(self.master, text="メイン画面に戻る", command=lambda: ViewController.switch_to_main_view(self.master))
        self.close_button.pack(pady=10)

    def fetch_data(self):
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()

        today = datetime.today().date()

        if end_date > today:
            end_date = today
            messagebox.showinfo("情報", "未来の日付が指定されているので、今日の日付にします。")

        fetch_controller = FetchController(self.master)

        try:
            fetch_controller.fetch_steps_and_sleep_in_range(start_date, end_date)
            messagebox.showinfo("完了", "データの取得が完了しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"データの取得中にエラーが発生しました。\n{e}")

