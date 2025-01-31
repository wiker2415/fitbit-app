import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ..controllers.view_controller import ViewController
from ..controllers.output_month_controller import OutputMonthController

class OutputMonthView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        self.master = master
        self.master.title("データ出力画面")

        # ウィンドウの大きさを指定
        window_width = 350
        window_height = 250

        # ウィンドウを画面中央に配置
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        pos_x = (screen_width // 2) - (window_width // 2)
        pos_y = (screen_height // 2) - (window_height // 2)
        self.master.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
        
        self.label = tk.Label(self.master, text="データ出力画面です。", wraplength=300)
        self.label.pack(pady=20)

        # 年月入力用フレーム
        self.date_frame = tk.Frame(self.master)
        self.date_frame.pack(anchor=tk.CENTER, pady=10)

        # 年選択用コンボボックス
        current_year = datetime.now().year
        years = [str(y) for y in range(2013, current_year + 1)]
        self.year_combobox = ttk.Combobox(self.date_frame, values=years, state="readonly", width=5)
        self.year_combobox.set(str(current_year))  # デフォルトで現在の年を選択
        self.year_combobox.pack(side=tk.LEFT, padx=2)
        self.year_label = tk.Label(self.date_frame, text="年", wraplength=5)
        self.year_label.pack(side=tk.LEFT)

        # 月選択用コンボボックス
        months = [str(m) for m in range(1, 13)]
        self.month_combobox = ttk.Combobox(self.date_frame, values=months, state="readonly", width=3)
        self.month_combobox.set(str(datetime.now().month))  # デフォルトで現在の月を選択
        self.month_combobox.pack(side=tk.LEFT, padx=2)
        self.month_label = tk.Label(self.date_frame, text="月", wraplength=5)
        self.month_label.pack(side=tk.LEFT)

        self.output_button = tk.Button(self.master, text="データを出力する", command=self.output_data)
        self.output_button.pack(pady=20)

        self.close_button = tk.Button(self.master, text="メイン画面に戻る", command=lambda: ViewController.switch_to_main_view(self.master))
        self.close_button.pack(pady=10)

    def output_data(self):
        year = int(self.year_combobox.get())
        month = int(self.month_combobox.get())
        
        output_month_controller = OutputMonthController(self.master, year, month, self.show_error)
        output_month_controller.start_plot()

    def show_error(self, error_message: str):
        """エラー時のコールバック"""
        messagebox.showerror("エラー", f"エラー: {error_message}")