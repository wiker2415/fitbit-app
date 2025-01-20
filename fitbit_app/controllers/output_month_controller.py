import os
import calendar
import datetime as dt
import jpholiday
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.lines import Line2D
import seaborn as sns
import threading
from ..views.progress_view import ProgressView
from ..models.output_month_service import OutputMonthService
from ..models.credential import Credential

# エラーログの設定
os.makedirs('error_log', exist_ok=True)

logging.basicConfig(
    filename='error_log/output_error.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# フォントを日本語対応のものに設定
rcParams['font.family'] = 'MS Gothic'
sns.set_theme(style='darkgrid', context='notebook', font='MS Gothic')

class OutputMonthController:
    def __init__(self, master, year: int, month: int, error_callback):
        self.master = master
        self.year = year
        self.month = month
        self.error_callback = error_callback

        # 月初と月末の日付を計算
        self.first_day_of_month = f"{self.year}-{self.month:02}-01"
        self.last_day = calendar.monthrange(self.year, self.month)[1]
        self.last_day_of_month = f"{self.year}-{self.month:02}-{self.last_day:02}"

        # 睡眠データと歩数データをセット
        try:
            output_month_service = OutputMonthService()
            output_month_service.retrieve_month_data(self.first_day_of_month, self.last_day_of_month)
            self.sleep_data = output_month_service.sleep_data
            self.step_data = output_month_service.step_data
        except Exception as e:
            # データベースが無い時
            if "no such table" in str(e):
                error_message = "データベースがありません。先にデータを取得してください。"
                self.error_callback(error_message)
            else:
                logging.error("An error occurred", exc_info=True)
                self.error_callback(str(e))
            raise Exception(f"{e}")

        # 保存フォルダ名をClient IDにする
        self.save_folder_name = Credential.client_id

    def start_plot(self):
        self.progress_view = ProgressView(self.master, "グラフ描画中です...")

        def run_task():
            try:
                self._plot_and_save_graph()
            except Exception as e:
                self.error_callback(str(e))
                raise Exception(f"{e}")
            finally:
                self.progress_view.close()

        # 新しいスレッドを使ってタスクを実行
        thread = threading.Thread(target=run_task)
        thread.start()
        
    def _plot_and_save_graph(self):
        """グラフを描画する
        """
        # A4用紙横向きの寸法(インチ単位)
        a4_height = 8.27
        a4_width = 11.69

        # グラフキャンバス用意
        fig = plt.figure(dpi=200, figsize=(a4_width, a4_height))

        # グラフ描画
        self._plot_sleep_data(fig, self.sleep_data)
        self._plot_step_data(fig, self.step_data)

        fig.tight_layout()

        # PDFで保存
        try:
            os.makedirs(fr'./graph/{self.save_folder_name}/monthly', exist_ok=True)

            # PDFに保存
            pdf_path = os.path.abspath(fr'./graph/{self.save_folder_name}/monthly/{self.year}-{self.month:02}.pdf')
            plt.savefig(pdf_path)

            # PDFが存在するか確認
            if not os.path.exists(pdf_path):
                logging.error("An error occurred", exc_info=True)
                raise Exception(f'PDFファイルが存在しません: {pdf_path}')

            # PDFを開く
            os.startfile(pdf_path)

        except PermissionError:
            raise Exception('ファイルが開かれているため、保存できません。\nPDFを閉じて再試行してください。')
        except Exception as e:
            logging.error("An error occurred", exc_info=True)
            raise Exception(f'ファイルの保存でエラーが発生しました。: {e}')
        finally:
            plt.clf()
            plt.close()

    def _plot_sleep_data(self, fig, sleep_data):
        """睡眠データをグラフに表示
        """
        # 睡眠グラフの色を辞書で指定
        COLORS_DICT = {
            'wake': 'red', 'awake': 'red',
            'rem': 'lightcyan', 'restless': 'lightcyan',
            'light': 'lightskyblue', 'asleep': 'lightskyblue',
            'deep': 'blue'
        }

        ax = fig.add_subplot(1, 3, (1, 2))

        # 凡例を設定
        self._add_sleep_legend(ax)

        # x軸目盛りの設定(00:00~24:00)
        ax.set_xlim([0, 86400]) # 秒数で指定
        xticks = [3600 * i for i in range(25)]
        xticklabels = [f'{i:02}:00' for i in range(25)]
        ax.set(xticks=xticks, xticklabels=xticklabels)
        ax.tick_params(axis='x', rotation=90)

        # y軸目盛りの設定
        self._setting_yaxis(ax)

        # ラベルの設定
        ax.set(xlabel='Time', ylabel='Date')
        ax.set_title(f'{self.year}年{self.month:02}月の睡眠データ')

        # 睡眠データのプロット
        for i in range(len(sleep_data)):
            for j in range(len(sleep_data[i])):
                date = sleep_data[i]['dateTime'].iloc[j].day
                start_sec = self._time_to_seconds(sleep_data[i]['dateTime'].iloc[j])
                width_sec = int(sleep_data[i]['seconds'].iloc[j])
                color = COLORS_DICT[sleep_data[i]['level'].iloc[j]]

                ax.barh(date, width_sec, left=start_sec, height=1, color=color, linewidth=0.3)

    def _time_to_seconds(self, datetime: dt.datetime) -> int:
        """与えられた日時を正午(00:00:00)からの秒数に変換し返す

        Args:
            datetime (dt.datetime): 日時

        Returns:
            int: 00:00:00 からの秒数
        """
        time_seconds = datetime.hour * 3600 + datetime.minute * 60 + datetime.second

        return time_seconds

    def _add_sleep_legend(self, ax):
        """睡眠データ用の凡例を設定
        """
        colors_dict = {
            'wake': 'red',
            'rem': 'lightcyan',
            'light': 'lightskyblue',
            'deep': 'blue'
        }

        legend_elements = [Line2D([0], [0], color=color, lw=4, label=label) for label, color in colors_dict.items()]
        ax.legend(handles=legend_elements, title='睡眠深さ')

    def _setting_yaxis(self, ax):
        """y軸の設定(01(日)~31(火)のような形)
        """
        yticks = []
        yticklabels = []
        ytick_daycolors = []

        # y軸目盛りの範囲設定(1~月末より1ずつ広くとらないと上手く収まってくれない)
        ax.set_ylim([0, self.last_day + 1])

        # y軸目盛りを01(日)のように設定する
        for day_int in range(1, self.last_day + 1):
            # y軸の値をリストに追加
            yticks.append(day_int)
            
            # y軸のラベルをリストに追加
            date = dt.date(self.year, self.month, day_int)
            yticklabels.append(f'{day_int:02}({self._get_day_of_week_jp(date)})')

            # y軸のラベルの色をリストに追加
            ytick_daycolors.append(self._get_color_of_day(date))

        ax.set(yticks=yticks, yticklabels=yticklabels)

        # 日付ごとに色を適用
        for yticklabel, daycolor in zip(ax.yaxis.get_ticklabels(), ytick_daycolors):
            yticklabel.set_color(daycolor)

        ax.invert_yaxis()

    def _get_day_of_week_jp(self, date: dt.date) -> str:
        """与えられた日付における曜日を日本語で返す

        Args:
            date (dt.date): 日付

        Returns:
            str: 日本語の曜日
        """
        week_list = ['月', '火', '水', '木', '金', '土', '日']

        return (week_list[date.weekday()])
    
    def _get_color_of_day(self, date: dt.date) -> str:
        """与えられた日付における曜日を判定し、
           平日ならblack、土曜ならblue、日曜・祝日はredを返す

        Args:
            date (dt.date): 日付

        Returns:
            str: 曜日の色(black, blue, red のいずれか)
        """
        if jpholiday.is_holiday(date) or date.weekday() == 6: # 日曜・祝日は赤
            return 'red'
        elif date.weekday() == 5: # 土曜は青
            return 'blue'
        else:
            return 'black' # 平日は黒
        
    def _plot_step_data(self, fig, step_data_df):
        """歩数データをグラフに表示
        """
        ax = fig.add_subplot(1, 3, 3)
        
        days = step_data_df['Date'].dt.day
        steps = step_data_df['Steps']
        ax.barh(days, steps, height=1.0, color='C0', label='歩数')

        # x軸の最大値を10000歩orそれ以上は自動に設定
        if len(steps) == 0 or max(steps) < 10000:
            plt.xlim([0, 10000])
            
        self._setting_yaxis(ax)

        #　ラベルの設定
        ax.set(xlabel='Steps', ylabel='Date')
        ax.set_title(f'{self.year}年{self.month:02}月の歩数データ')
        
        ax.legend()