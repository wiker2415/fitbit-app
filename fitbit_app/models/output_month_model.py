import sqlite3
from sqlite3 import Error
from .credential import Credential

class OutputMonthModel:
    def __init__(self):
        self.sleep_data = None
        self.step_data = None

        self.db_name = fr"./database/{Credential.client_id}.db"
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        except Error as e:
            raise Exception(f"データベースに接続できませんでした: {e}")
        
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def retrieve_month_data(self, first_day_of_month: str, last_day_of_month: str) -> None:
        """データベースから月毎のデータを取得する

        Args:
            first_day_of_month (str): 月初の日付
            last_day_of_month (str): 月末の日付
        """
        self.sleep_data = self._retrieve_month_sleep_data(first_day_of_month, last_day_of_month)
        self.step_data = self._retrieve_month_step_data(first_day_of_month, last_day_of_month)

    def _retrieve_month_sleep_data(self, first_day_of_month: str, last_day_of_month: str) -> str:
        """月毎の睡眠データを取得する

        Args:
            first_day_of_month (str): 月初の日付
            last_day_of_month (str): 月末の日付

        Raises:
            Exception: 睡眠データの取得エラー

        Returns:
            str: 睡眠データ
        """
        try:
            self.cursor.execute('''
                SELECT sleep_data FROM sleep_data
                WHERE date BETWEEN ? AND ?
                ORDER BY date
            ''', (first_day_of_month, last_day_of_month))
            rows = self.cursor.fetchall()
            return rows
        except Error as e:
            raise Exception(f"睡眠データの取得でエラーが起きました。: {e}")
        
    def _retrieve_month_step_data(self, first_day_of_month: str, last_day_of_month: str) -> str:
        """月毎の歩数データを取得する

        Args:
            first_day_of_month (str): 月初の日付
            last_day_of_month (str): 月末の日付

        Raises:
            Exception: 歩数の取得エラー

        Returns:
            str: 歩数データ
        """
        try:
            self.cursor.execute('''
                SELECT date, step_count FROM step_data
                WHERE date BETWEEN ? AND ?
                ORDER BY date
            ''', (first_day_of_month, last_day_of_month))
            rows = self.cursor.fetchall()
            return rows
        except Error as e:
            raise Exception(f"歩数データの取得でエラーが起きました。: {e}")

