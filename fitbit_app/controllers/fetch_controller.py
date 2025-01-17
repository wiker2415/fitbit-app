from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from fitbit import Fitbit
from fitbit.exceptions import HTTPTooManyRequests
import logging
import os
import threading
from ..views.progress_view import ProgressView
from ..models.credential import Credential
from ..models.fetch_model import FetchModel

os.makedirs('error_log', exist_ok=True)

logging.basicConfig(
    filename='error_log/fetch_error.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class FetchController:
    def __init__(self, master, start_date, end_date, error_callback, success_callback):
        self.fitbit = Fitbit(
            Credential.client_id,
            Credential.client_secret,
            Credential.access_token,
            Credential.refresh_token
        )
        
        self.master = master
        self.start_date = start_date
        self.end_date = end_date
        self.error_callback = error_callback
        self.success_callback = success_callback

    def start_fetch(self):
        self.progress_view = ProgressView(self.master, "データ取得中です...")

        def run_task():
            try:
                self._fetch_steps_and_sleep_data_in_range()
                self.success_callback()
            except Exception as e:
                self.error_callback(str(e))
            finally:
                self.progress_view.close()

        thread = threading.Thread(target=run_task)
        thread.start()

    def _fetch_steps_and_sleep_data_in_range(self):
        total_days = (self.end_date - self.start_date).days + 1
        if total_days > 100:
            raise Exception(f"取得する日数が多すぎます。3ヵ月分程度に絞ってください。")
        
        futures = [] # タスクの例外はfuture.result()を呼び出さないとキャッチできない

        with ThreadPoolExecutor(max_workers=50) as executor:
            for i in range(total_days):
                current_date = self.start_date + timedelta(days=i)
                futures.append(
                    executor.submit(self._fetch_and_save_data, current_date)
                )
            
        # タスクの結果を確認し、例外があれば再スロー
        for future in futures:
            try:
                future.result()  # ここで例外が発生していればキャッチできる
            except Exception as e:
                raise Exception(f"{e}")

    def _fetch_and_save_data(self, date):
        model = FetchModel()

        date_str = date.isoformat()

        # データの取得
        step_count = self._fetch_step_data(date)
        sleep_data = self._fetch_sleep_data(date)

        # データベースへ保存
        try:
            model.insert_step_data(date_str, step_count)
            model.insert_sleep_data(date_str, sleep_data)
        except Exception as e:
            logging.error("An save error occurred", exc_info=True)
            raise Exception(
                f"{date_str} のデータ保存に失敗しました。\n"
                f"詳細: {e}"
            )
        finally:
            model.close()

    def _fetch_step_data(self, date):
        try:
            step_data = self.fitbit.intraday_time_series(
                'activities/steps', date, detail_level='15min'
            )
            step_count = step_data['activities-steps'][0]['value']
            
            return step_count
        except (HTTPTooManyRequests, KeyError) as e:
            raise Exception(
                    f"{date.isoformat()}の歩数データを取得できませんでした。\n"
                    f"原因: サーバーへのアクセスが多すぎます。\n"
                    f"{f'1時間後に再度実行してください。'}"
                )
        except Exception as e:
            logging.error("An fetch step data error occurred", exc_info=True)
            raise Exception(
                f"{date.isoformat()}の歩数データを取得できませんでした。\n"
                f"詳細: {e}"
            )
    
    def _fetch_sleep_data(self, date):
        try:
            sleep_data = []

            raw_sleep_data = self.fitbit.get_sleep(date)
            sleep_count = raw_sleep_data['summary']['totalSleepRecords']

            for i in reversed(range(sleep_count)):
                sleep_data.append(raw_sleep_data['sleep'][i]['levels']['data'])

            return str(sleep_data)
        except (HTTPTooManyRequests, KeyError) as e:
            raise Exception(
                    f"{date.isoformat()}の睡眠データを取得できませんでした。\n"
                    f"原因: サーバーへのアクセスが多すぎます。\n"
                    f"{f'1時間後に再度実行してください。'}"
                )
        except Exception as e:
            logging.error("An fetch sleep data error occurred", exc_info=True)
            raise Exception(
                f"{date.isoformat()}の睡眠データを取得できませんでした。\n"
                f"詳細: {e}"
            )

