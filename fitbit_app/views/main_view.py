import tkinter as tk
from ..controllers.view_controller import ViewController

class MainView:
    def __init__(self, root):
        self.root = root
        self.root.title("Fitbit アプリ メイン画面")

        # ウィンドウの大きさを指定
        window_width = 350
        window_height = 250

        # ウィンドウを画面中央に配置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        pos_x = (screen_width // 2) - (window_width // 2)
        pos_y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
        
        # ラベルとボタンの追加
        self.label = tk.Label(self.root, text="認証が成功しました。", wraplength=300)
        self.label.pack(pady=20)

        self.fetch_button = tk.Button(self.root, text="データを取得する", command=lambda: ViewController.switch_to_fetch_view(self.root))
        self.fetch_button.pack(pady=10)

        self.output_button = tk.Button(self.root, text="データを出力する", command=lambda: ViewController.switch_to_output_month_view(self.root))
        self.output_button.pack(pady=10)

        self.close_button = tk.Button(self.root, text="閉じる", command=lambda: ViewController.close_view(self.root))
        self.close_button.pack(pady=20)


