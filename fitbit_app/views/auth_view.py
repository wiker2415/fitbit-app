import tkinter as tk
from tkinter import messagebox
import re
import json
import os
from ..controllers.auth_controller import OAuth2Controller
from ..controllers.view_controller import ViewController
from ..models.client_state import ClientState

class AuthView:
    def __init__(self, root):
        self.root = root
        self.root.title("認証フォーム")

        # 前回の認証情報を保存するJSONファイルの保存パス
        self.credentials_file = "credentials.json"

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
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        pos_x = (screen_width // 2) - (window_width // 2)
        pos_y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

    def _set_validation_commands(self):
        # 入力制限用のvalidatecommandを設定
        self.validate_id = self.root.register(self._validate_client_id)
        self.validate_secret = self.root.register(self._validate_client_secret)

    def _create_widgets(self):
        # Client ID 入力欄
        self.client_id_label = tk.Label(self.root, text="Client ID :")
        self.client_id_label.pack(pady=(10, 0))
        self.client_id_entry = tk.Entry(self.root, width=35, validate='key', validatecommand=(self.validate_id, '%P'))
        self.client_id_entry.pack(pady=5)

        # Client Secret 入力欄
        self.client_secret_label = tk.Label(self.root, text="Client Secret :")
        self.client_secret_label.pack(pady=(10, 0))
        self.client_secret_entry = tk.Entry(self.root, width=35, show="*", validate='key', validatecommand=(self.validate_secret, '%P'))
        self.client_secret_entry.pack(pady=5)

        # 保存オプション
        self.save_credentials_var = tk.BooleanVar()
        self.save_credentials_check = tk.Checkbutton(
            self.root, text="次回の認証のためにクライアント情報を保存する", variable=self.save_credentials_var
        )
        self.save_credentials_check.pack(pady=15)

        # 認証ボタン
        self.auth_button = tk.Button(self.root, text="認証", command=self.authenticate, width=20, height=2)
        self.auth_button.pack(pady=5)

    def authenticate(self):
        client_id = self.client_id_entry.get()
        client_secret = self.client_secret_entry.get()

        if not client_id or not client_secret:
            messagebox.showerror("エラー", "Client ID と Client Secret を入力してください。")
            return
        
        controller = OAuth2Controller(client_id, client_secret)
        authorize_message = controller.browser_authorize()
        
        if authorize_message == '認証成功':
            # 保存オプションがオンならJSONファイルに保存する
            if self.save_credentials_var.get():
                self._save_credentials(client_id, client_secret)
            else:
                self._delete_credentials()

            ClientState.client_id = client_id
            ClientState.client_secret = client_secret

            ViewController.switch_to_main_view(self.root)
        else:
            messagebox.showerror("エラー", authorize_message)

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
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'r') as file:
                try:
                    data = json.load(file)
                    self.client_id_entry.insert(0, data.get("client_id", ""))
                    self.client_secret_entry.insert(0, data.get("client_secret", ""))
                    self.save_credentials_var.set(True)
                except json.JSONDecodeError:
                    pass

    def _save_credentials(self, client_id, client_secret):
        data = {
            "client_id": client_id,
            "client_secret": client_secret
        }
        with open(self.credentials_file, 'w') as file:
            json.dump(data, file)

    def _delete_credentials(self):
        if os.path.exists(self.credentials_file):
            os.remove(self.credentials_file)