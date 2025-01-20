import requests
import webbrowser
import threading
from fitbit import Fitbit
from urllib.parse import urlparse
import cherrypy
from oauthlib.oauth2.rfc6749.errors import InvalidClientError
from ..models.credential import Credential

class OAuth2Controller:
    SUCCESS_HTML = '''
        <h1>Fitbit APIへのアクセスが許可されました。</h1><br/>
        <h3>ウィンドウを閉じてください。</h3>
        '''
    FAILURE_HTML = '''
        <h1>エラーが発生しました。</h1><br/>
        <h3>{error_message}</h3></br>
        <h3>ウィンドウを閉じてください。</h3>
    '''

    def __init__(self, error_callback, success_callback, redirect_uri='http://127.0.0.1:8080/'):
        self.redirect_uri = redirect_uri
        self.fitbit = Fitbit(
            Credential.client_id,
            Credential.client_secret,
            redirect_uri=self.redirect_uri,
            timeout=10
        )
        self.error_callback = error_callback
        self.success_callback = success_callback
    
    def browser_authorize(self):
        """認証URLをブラウザで開き、レスポンスを受け取るためにCherryPyサーバーを起動する"""
        def browser_task():
            url, _ = self.fitbit.client.authorize_token_url()
            # 認証URLが正しいか確認(Client情報が間違っていると500エラー)
            try:
                if self._check_url_connection(url) != 200:
                    self.error_callback('エラーです。Client情報を確認してください。')
                    return
            except Exception as e:
                self.error_callback(
                    f'サーバーへの接続でエラーが起こりました。\n'
                    f'詳細: {e}'
                )
                return

            webbrowser.open(url)

            # CherryPyサーバーを起動して認証を待つ
            urlparams = urlparse(self.redirect_uri)
            cherrypy.config.update({
                'server.socket_host': urlparams.hostname,
                'server.socket_port': urlparams.port,
            })

            cherrypy.quickstart(self, '/')

        thread = threading.Thread(target=browser_task)
        thread.start()

    @cherrypy.expose
    def index(self, state, code=None, error=None):
        """Fitbitからの認証コードを受け取ってアクセストークンを取得"""
        if code:
            try:
                self.fitbit.client.fetch_access_token(code)

                # トークンの取得
                access_token = self.fitbit.client.session.token['access_token']
                refresh_token = self.fitbit.client.session.token['refresh_token']
                expires_at = self.fitbit.client.session.token['expires_at']

                Credential.access_token = access_token
                Credential.refresh_token = refresh_token
                Credential.expires_at = expires_at

                self.success_callback()

                return self.SUCCESS_HTML
            except InvalidClientError as e:
                error_message = 'エラーです。Client情報を確認してください。'
                self.error_callback(error_message)
                return self.FAILURE_HTML.format(error_message=error_message)
            except Exception as e:
                error_message = f'予期せぬエラー: {str(e)}'
                self.error_callback(error_message)
                return self.FAILURE_HTML.format(error_message=error_message)
            finally:
                self._shutdown_cherrypy()
        else:
            error_message = '予期せぬエラーです。'
            self.error_callback(error_message)
            self._shutdown_cherrypy()
            return self.FAILURE_HTML.format(error_message=error_message)

    def _shutdown_cherrypy(self):
        """cherrypyサーバーを終了"""
        if cherrypy.engine.state == cherrypy.engine.states.STARTED:
            cherrypy.engine.exit()

    def _check_url_connection(self, url):
        response = requests.get(url, timeout=10)
        return response.status_code