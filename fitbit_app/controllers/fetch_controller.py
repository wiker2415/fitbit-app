from fitbit import Fitbit
from datetime import datetime, timedelta
from ..models.credential import Credential
from ..models.fetch_model import FetchModel

class FetchController:
    def __init__(self):
        self.fitbit = Fitbit(
                Credential.client_id,
                Credential.client_secret,
                Credential.access_token,
                Credential.refresh_token
            )
        self.model = FetchModel()

    def fetch_steps_and_sleep_in_range(self, start_date, end_date):
        start_date = datetime.strptime(start_date, "%Y/%m/%d").date()
        end_date = datetime.strptime(end_date, "%Y/%m/%d").date()

        current_date = start_date
        while current_date <= end_date:
            try:
                self._fetch_step_data(current_date)
                self._fetch_sleep_data(current_date)
            except Exception as e:
                raise Exception(f"{current_date} のデータ取得に失敗しました。: {e}")

            current_date += timedelta(days=1)
        
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
