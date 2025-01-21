# ソースコードを実行可能にするための設定
- PythonをインストールしたWindowsパソコンを用意<br>
(Macは動作確認していません)

- 仮想環境を作成する<br>
```python -m venv venv```

- 仮想環境をアクティベート<br>
```.\venv\Scripts\activate```

- パッケージをインストール<br>
```pip install -r requirements.txt```

- Fitbitパッケージのバージョンを1.2に変更する<br>
./venv/Lib/fitbit/api.pyを開く<br>
API_VERSION と検索し、<br>
API_VERSION = 1 を API_VERSION = 1.2 に変更する(2か所)<br>