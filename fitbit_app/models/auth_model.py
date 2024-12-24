import sqlite3
from sqlite3 import Error

class AuthModel:
    def __init__(self, db_name='auth.db'):
        self.db_name = db_name
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.create_tables()
        except Error as e:
            print(f"データベースに接続できませんでした。: {e}")

    def create_tables(self):
        """ テーブルが存在しない場合に作成する """
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL UNIQUE,
                    client_secret TEXT NOT NULL
                );
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL UNIQUE,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE             
                );
            ''')
            self.conn.commit()
        except Error as e:
            print(f"テーブル作成でエラーが起きました。: {e}")

    def insert_clients(self, client_id, client_secret):
        """clientsテーブルにclient_idとclient_secretを保存。client_idが存在するときはUNIQUEなのでスキップ"""
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO clients (client_id, client_secret)
                VALUES (?, ?)
            ''', (client_id, client_secret))
            self.conn.commit()
        except Error as e:
            print(f"クライアント情報の挿入でエラーが起きました。: {e}")

    def insert_tokens(self, client_id, access_token, refresh_token, expires_at):
        """tokensテーブルにaccess_tokenとrefresh_tokenを保存。client_idが存在する場合は更新する"""
        try:
            self.cursor.execute('''
                INSERT INTO tokens (client_id, access_token, refresh_token, expires_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(client_id) DO UPDATE SET
                    access_token = excluded.access_token,
                    refresh_token = excluded.refresh_token,
                    expires_at = excluded.expires_at
            ''', (client_id, access_token, refresh_token, expires_at))
            self.conn.commit()
        except Error as e:
            print(f"トークン情報の挿入でエラーが起きました。: {e}")
    
    def close(self):
        self.conn.close()
