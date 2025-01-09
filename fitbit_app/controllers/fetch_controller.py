from fitbit import Fitbit
from datetime import timedelta
from ..views.progressbar_view import ProgressbarView
from ..models.credential import Credential
from ..models.fetch_model import FetchModel

class FetchController:
    def __init__(self, master):
        self.fitbit = Fitbit(
                Credential.client_id,
                Credential.client_secret,
                Credential.access_token,
                Credential.refresh_token
            )
        
        self.master = master

    def fetch_steps_and_sleep_in_range(self, start_date, end_date):
        self.model = FetchModel()

        total_days = (end_date - start_date).days + 1

        progressbar_view = ProgressbarView(self.master, total_days)

        for i in range(total_days):
            current_date = start_date + timedelta(days=i)
            progressbar_view.update_progress(i, current_date)
            try:
                self._fetch_step_data(current_date)
                self._fetch_sleep_data(current_date)

            except Exception as e:
                if 'Too Many Requests' in str(e):
                    raise Exception(f"{current_date} のデータ取得に失敗しました。: {e}\nアクセスが多すぎるので、1時間後に再度実行してください。")
                else:
                    raise Exception(f"{current_date} のデータ取得に失敗しました。: {e}")
                
        self.model.close()
        
    def _fetch_step_data(self, date):
        step_data = self.fitbit.intraday_time_series(
                'activities/steps', date, detail_level='15min'
            )
        step_count = step_data['activities-steps'][0]['value']

        self.model.insert_step_data(date.isoformat(), step_count)
    
    def _fetch_sleep_data(self, date):
        sleep_data = []

        raw_sleep_data = self.fitbit.get_sleep(date)
        sleep_count = raw_sleep_data['summary']['totalSleepRecords']

        for i in reversed(range(sleep_count)):
            sleep_data.append(raw_sleep_data['sleep'][i]['levels']['data'])

        self.model.insert_sleep_data(date.isoformat(), str(sleep_data))
