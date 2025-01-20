import threading
import tkinter as tk
from tkinter import messagebox
import re
from ..controllers.auth_controller import OAuth2Controller
from ..controllers.view_controller import ViewController
from ..models.credential import Credential
from ..models.auth_model import AuthModel

class AuthView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        self.master = master
        self.master.title("認証フォーム")

        self.auth_model = AuthModel()

        # ウィンドウの設定
        self._set_window_geometry()

        # 入力制限用のvalidatecommandを設定
        self._set_validation_commands()

        # ウィジェットを配置
        self._create_widgets()

        # JSONファイルを読み込み
        self._load_credentials()

    def _set_window_geometry(self):
        # ウィンドウの大きさを指定
        window_width = 350
        window_height = 250

        #ウィンドウを画面中央に配置
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        pos_x = (screen_width // 2) - (window_width // 2)
        pos_y = (screen_height // 2) - (window_height // 2)
        self.master.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

    def _set_validation_commands(self):
        # 入力制限用のvalidatecommandを設定
        self.validate_id = self.master.register(self._validate_client_id)
        self.validate_secret = self.master.register(self._validate_client_secret)

    def _create_widgets(self):
        # Client ID 入力欄
        self.client_id_label = tk.Label(self.master, text="Client ID :")
        self.client_id_label.pack(pady=(10, 0))
        self.client_id_entry = tk.Entry(self.master, width=35, validate='key', validatecommand=(self.validate_id, '%P'))
        self.client_id_entry.pack(pady=5)

        # Client Secret 入力欄
        self.client_secret_label = tk.Label(self.master, text="Client Secret :")
        self.client_secret_label.pack(pady=(10, 0))
        self.client_secret_entry = tk.Entry(self.master, width=35, show="*", validate='key', validatecommand=(self.validate_secret, '%P'))
        self.client_secret_entry.pack(pady=5)

        # 保存オプション
        self.save_credentials_var = tk.BooleanVar()
        self.save_credentials_check = tk.Checkbutton(
            self.master, text="次回の認証のためにクライアント情報を保存する", variable=self.save_credentials_var
        )
        self.save_credentials_check.pack(pady=15)

        # 認証ボタン
        self.auth_button = tk.Button(self.master, text="認証", command=self.authenticate, width=20, height=2)
        self.auth_button.pack(pady=5)

    def authenticate(self):
        self.client_id = self.client_id_entry.get()
        self.client_secret = self.client_secret_entry.get()

        if not self.client_id or not self.client_secret:
            messagebox.showerror("エラー", "Client ID と Client Secret を入力してください。")
            return
        
        # 資格情報をCredentialクラスに保存
        Credential.client_id = self.client_id
        Credential.client_secret = self.client_secret

        auth_controller = OAuth2Controller(self.error_callback, self.success_callback)
        auth_controller.browser_authorize()

    def error_callback(self, error_message: str):
        """エラー時のコールバック"""
        def show_error_message():
            messagebox.showerror("エラー", f"エラー: {error_message}")
        
        thread = threading.Thread(target=show_error_message)
        thread.start()
    
    def success_callback(self):
        """認証成功時のコールバック"""
        def success_task():
            # 保存オプションがオンならJSONファイルに保存する
            if self.save_credentials_var.get():
                self.auth_model.save_credentials(self.client_id, self.client_secret)
            else:
                self.auth_model.delete_credentials()

            # メインスレッドでUI操作を行う
            self.master.after(0, ViewController.switch_to_main_view, self.master)

        thread = threading.Thread(target=success_task)
        thread.start()
            

    def _validate_client_id(self, new_value):
        # client_idは10文字以内で、半角英数字のみ
        if len(new_value) <= 10 and re.fullmatch(r"[a-zA-Z0-9]*", new_value):
            return True
        return False
    
    def _validate_client_secret(self, new_value):
        # client_secretは40文字以内で、半角英数字のみ
        if len(new_value) <= 40 and re.fullmatch(r"[a-zA-Z0-9]*", new_value):
            return True
        return False
    
    def _load_credentials(self):
        """JSONファイルを読み込み、フォームに入力しておく
        """
        credencials = self.auth_model.load_credentials()

        self.client_id_entry.insert(0,credencials.get("client_id", ""))
        self.client_secret_entry.insert(0, credencials.get("client_secret", ""))

        self.save_credentials_var.set(bool(credencials))