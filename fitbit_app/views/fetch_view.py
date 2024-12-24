import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from ..controllers.view_controller import ViewController
from ..models.client_state import ClientState

class FetchView:
    def __init__(self, root):
        self.root = root
        self.root.title("データ取得画面")

        # ウィンドウの大きさを指定
        window_width = 350
        window_height = 300

        # ウィンドウを画面中央に配置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        pos_x = (screen_width // 2) - (window_width // 2)
        pos_y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
        
        label = tk.Label(self.root, text="データ取得画面です。", wraplength=300)
        label.pack(pady=20)

        # 開始日入力フォーム
        self.start_date_frame = tk.Frame(self.root)
        self.start_date_frame.pack(anchor=tk.CENTER, pady=10)
        self.start_date_label = tk.Label(self.start_date_frame, text="開始日: ")
        self.start_date_label.pack(side=tk.LEFT, padx=5)
        self.start_date_entry = DateEntry(self.start_date_frame, showweeknumbers=False, date_pattern="yyyy/mm/dd", locale='ja_JP')
        self.start_date_entry.pack(side=tk.LEFT, padx=5)

        # 終了日入力フォーム
        self.end_date_frame = tk.Frame(self.root)
        self.end_date_frame.pack(anchor=tk.CENTER, pady=10)
        self.end_date_label = tk.Label(self.end_date_frame, text="終了日: ")
        self.end_date_label.pack(side=tk.LEFT, padx=5)
        self.end_date_entry = DateEntry(self.end_date_frame, showweeknumbers=False, date_pattern="yyyy/mm/dd", locale='ja_JP')
        self.end_date_entry.pack(side=tk.LEFT, padx=5)

        self.fetch_button = tk.Button(self.root, text="データを取得する", command=self.fetch_data)
        self.fetch_button.pack(pady=20)

        self.close_button = tk.Button(self.root, text="メイン画面に戻る", command=lambda: ViewController.switch_to_main_view(self.root))
        self.close_button.pack(pady=10)

    def fetch_data(self):
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        client_id = ClientState.client_id
        client_secret = ClientState.client_secret

        access_token = ClientState.access_token
        refresh_token = ClientState.refresh_token

        messagebox.showinfo("入力値", f"入力された値: {access_token}, {refresh_token}")

