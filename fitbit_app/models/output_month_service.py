import ast
import datetime as dt
import pandas as pd
import numpy as np
from .output_month_model import OutputMonthModel

class OutputMonthService:
    def __init__(self):
        self.sleep_data = None
        self.step_data = None

    def retrieve_month_data(self, first_day_of_month: str, last_day_of_month: str) -> None:
        """データベースから月毎のデータを取得する

        Args:
            first_day_of_month (str): 月初の日付
            last_day_of_month (str): 月末の日付
        """
        # データベースから睡眠と歩数のデータを取得
        output_month_model = OutputMonthModel()
        output_month_model.retrieve_month_data(first_day_of_month, last_day_of_month)
        self.sleep_data = output_month_model.sleep_data
        self.step_data = output_month_model.step_data
        output_month_model.close()

        # 睡眠データを変換(生データ→データフレーム→24時間スケール)
        self.sleep_data = self._convert_sleep_list_to_dataframe(self.sleep_data)
        self.sleep_data = self._convert_sleep_data_df_to_24h_scale(self.sleep_data)

        # 歩数データを変換(生データ→リスト)
        self.step_data = self._convert_step_data_to_list(self.step_data)

    def _convert_sleep_list_to_dataframe(self, sleep_data: list) -> list:
        """睡眠データをデータフレームに変換
           同時にグラフ化に必要な加工をする

        Args:
            sleep_data (list): データベースから取り出したままの睡眠データのリスト

        Returns:
            list: 睡眠データの詳細をデータフレーム化したリスト
        """
        convert_sleep_data = []

        # まずは睡眠データの詳細ひとつひとつをlist型に変換する
        for i in range(len(sleep_data)): # 1日ごとのデータに分ける
            for j in range(len(sleep_data[i])): 
                # タプルから取り出すと文字列が出てくる
                data_str = sleep_data[i][j]
                # 文字列をリストに変換
                data_list = ast.literal_eval(data_str)
                convert_sleep_data.append(data_list)

        # 詳細データをデータフレームに変換し、必要な加工をする
        for i in range(len(convert_sleep_data)):
            for j in range(len(convert_sleep_data[i])):
                # データフレームに変換
                convert_sleep_data[i][j] = pd.DataFrame(convert_sleep_data[i][j])

                # 日付の列(dateTime列)を文字列からdatetime型に変換する
                convert_sleep_data[i][j]['dateTime'] = pd.to_datetime(convert_sleep_data[i][j]['dateTime'], format='%Y-%m-%dT%H:%M:%S.%f')

                # グラフ化に必要なので、最終行のdateTimeにsecondsを足したものを末尾に追加
                end_time = convert_sleep_data[i][j]['dateTime'].iloc[-1]  # 最終行の時刻
                level = convert_sleep_data[i][j]['level'].iloc[-1]        # 最終行の睡眠レベル
                time_delta = convert_sleep_data[i][j]['seconds'].iloc[-1] # 最終行の継続秒
                time_delta = np.timedelta64(time_delta, 's')
                new_end_time = end_time + time_delta
                convert_sleep_data[i][j].loc[len(convert_sleep_data[i][j])] = [new_end_time, level, 0] # 最終行に追加

        return convert_sleep_data
    
    def _convert_sleep_data_df_to_24h_scale(self, sleep_data_df: list) -> list:
        """睡眠データのリストを24hのスケールに変換する。
           例えば、3日の睡眠が22:00~7:00の場合、3日のデータに22:00~7:00と記録される。
           これはグラフを書くときに都合が悪いので、
           2日のデータに22:00~23:59を追加し、3日のデータは0:00~7:00というように
           データを加工する。

        Args:
            sleep_data (list): 睡眠データをデータフレーム化したリスト

        Returns:
            list: 24hスケールに直したデータフレームのリスト
        """
        sleep_24h_df = []

        for i in range(len(sleep_data_df)): # 日付ごと
            for j in range(len(sleep_data_df[i])): # 睡眠回ごと
                # 最終行の日付(当日)を取得
                current_day = sleep_data_df[i][j]['dateTime'].iloc[-1].date()

                # 当日分と前日分のデータを保存する変数を用意、両方ともデータをつめておく
                current_day_df = sleep_data_df[i][j]
                previous_day_df = sleep_data_df[i][j]

                for k in range(len(sleep_data_df[i][j])):
                    sleep_row = sleep_data_df[i][j].loc[k] # 行ごとのデータ
                    sleep_row_day = sleep_row['dateTime'].date() # その行の日付

                    # 当日部分を current_day_df、前日部分を previous_day_df にするため、
                    # その行が当日のデータなら previous_day_df から削除
                    # そうでなければ current_day_df から削除する
                    if sleep_row_day != current_day:
                        current_day_df = current_day_df.drop(k)
                    else:
                        previous_day_df = previous_day_df.drop(k)

                # previous_day_df が存在したら
                if not previous_day_df.empty:
                    # previous_day_df の最終行に23:59:59を追加する
                    previous_day_last_dateTime = previous_day_df['dateTime'].iloc[-1]
                    previous_day_last_level = previous_day_df['level'].iloc[-1]

                    # 月初の0時前のデータを追加しないためのif
                    if previous_day_last_dateTime.month == current_day.month:

                        previous_day_midnight = dt.datetime(
                            previous_day_last_dateTime.year,
                            previous_day_last_dateTime.month,
                            previous_day_last_dateTime.day,
                            23, 59, 59
                        )
                        
                        time_delta_midnight_seconds = int(
                            (previous_day_midnight - previous_day_last_dateTime)
                            .total_seconds()
                        )

                        previous_day_df.loc[len(previous_day_df) - 1] = [
                            previous_day_last_dateTime,
                            previous_day_last_level,
                            time_delta_midnight_seconds
                        ]
                        
                        previous_day_df.loc[len(previous_day_df)] = [
                            previous_day_midnight,
                            previous_day_last_level,
                            0
                        ]

                        sleep_24h_df.append(previous_day_df)

                    # current_day_df の先頭行に00:00:00を追加する
                    current_day_first_datetime = current_day_df['dateTime'].iloc[0]

                    current_day_midnight = dt.datetime(
                        current_day_first_datetime.year,
                        current_day_first_datetime.month,
                        current_day_first_datetime.day,
                        00, 00, 00
                    )
                    
                    time_delta_midnight_seconds = int(
                            (current_day_first_datetime - current_day_midnight)
                            .total_seconds()
                        )
                    
                    new_first_row = pd.DataFrame({
                        'dateTime': current_day_midnight,
                        'level': previous_day_last_level,
                        'seconds': time_delta_midnight_seconds
                    }, index=[0])

                    # インデックスをふり直したいのでconcatで結合
                    current_day_df = pd.concat([new_first_row, current_day_df], ignore_index=True)

                sleep_24h_df.append(current_day_df)

        return sleep_24h_df

    def _convert_step_data_to_list(self, step_data: list) -> list:
        return [x[0] for x in step_data]
