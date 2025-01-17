import json
import os

class AuthModel:
    def __init__(self):
        self.credentials_file_dir = f"./database"
        os.makedirs(self.credentials_file_dir, exist_ok=True)

        # JSONファイルのパスを指定
        self.credentials_file = os.path.join(self.credentials_file_dir, f"credentials.json")

    def load_credentials(self) -> dict:
        """JSONファイルからクライアント情報を読み込む

        Returns:
            dict: クライアント情報の辞書（例: {"client_id": "abc", "client_secret": "xyz"}）または空辞書。
        """
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'r') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return {}
        return {}

    def save_credentials(self, client_id: str, client_secret: str):
        """JSONファイルにクライアント情報を保存する

        Args:
            client_id (str): Client ID
            client_secret (str): Client Secret
        """
        data = {
            "client_id": client_id,
            "client_secret": client_secret
        }
        with open(self.credentials_file, 'w') as file:
            json.dump(data, file)

    def delete_credentials(self):
        """JSONファイルを削除する
        """
        if os.path.exists(self.credentials_file):
            os.remove(self.credentials_file)