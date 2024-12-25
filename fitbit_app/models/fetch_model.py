import sqlite3
from sqlite3 import Error
from ..models.credential import Credential

class FetchModel:
    CREATE_STEP_TABLE = '''
        CREATE TABLE IF NOT EXISTS step_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            step_count INT
        )
    '''
    CREATE_SLEEP_TABLE = '''
        CREATE TABLE IF NOT EXISTS sleep_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            sleep_data TEXT
        )
    '''
    
    def __init__(self):
        self.db_name = f"{Credential.client_id}.db"
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.create_tables()
        except Error as e:
            raise Exception(f"データベースに接続できませんでした: {e}")

    def close_resources(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def __del__(self):
        self.close_resources()

    def create_tables(self):
        try:
            self.cursor.execute(self.CREATE_STEP_TABLE)
            self.cursor.execute(self.CREATE_SLEEP_TABLE)
            self.conn.commit()
        except Error as e:
            raise Exception(f"テーブル作成に失敗しました: {e}")

    def insert_step_data(self, date, step_count):
        try:
            self.cursor.execute('''
                INSERT INTO step_data (date, step_count)
                VALUES (?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    date = excluded.date,
                    step_count = excluded.step_count
            ''', (date, step_count))
            self.conn.commit()
        except Error as e:
            raise Exception(f"歩数データの挿入に失敗しました。: {e}")

    def insert_sleep_data(self, date, sleep_data):
        try:
            self.cursor.execute('''
                INSERT INTO sleep_data (date, sleep_data)
                VALUES (?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    date = excluded.date,
                    sleep_data = excluded.sleep_data
            ''', (date, sleep_data))
            self.conn.commit()
        except Error as e:
            raise Exception(f"歩数データの挿入に失敗しました。: {e}")