from cachetools import TTLCache
import logging
import requests
import webbrowser
from urllib.parse import urlparse, parse_qs
import base64
import threading
import http.server
import socketserver
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


AUTH_ENDPOINT = 'https://accounts.spotify.com/authorize'
TOKEN_ENDPOINT = 'https://accounts.spotify.com/api/token'
REDIRECT_URL = 'http://localhost:8080'

API_BASE_URL = 'https://api.spotify.com/v1'


class SpoPyAPI:

    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or os.getenv('CLIENT_ID')
        self.client_secret = client_secret or os.getenv('CLIENT_SECRET')
        self._auth_code = None
        self.refresh_token: str = None
        self.ttl_cache = TTLCache(maxsize=1, ttl=3600)
        self.authorize()

    def _get_request(self, url, params=None):
        logger.info('Get URL: %s', url)
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}'
        }
        result = requests.get(url, headers=headers, params=params)
        result.raise_for_status()
        return result.json()

    def authorize(self):
        """
        Oauth2 authorization.
        """
        if not self.client_id:
            logger.error('No client id.')
            return None

        server_thread = threading.Thread(target=self._start_local_server)
        server_thread.start()

        auth_params = {
            'client_id': self.client_id,
            'redirect_uri': REDIRECT_URL,
            'scope': 'user-library-read',
            'response_type': 'code',
        }
        query_params = '&'.join([f'{k}={v}' for k, v in auth_params.items()])
        auth_url = f"{AUTH_ENDPOINT}?{query_params}"

        logger.info('Start authorization..')
        webbrowser.open(auth_url)
        server_thread.join()
        logger.info('Authorization done, closing server.')

        if not self._auth_code:
            logger.error('Login failed, no authorization code token.')
            return None
        
        self.get_access_token(self._auth_code)

    def _start_local_server(self):
        # Start a local server to handle the Spotify callback
        server = SpotifyAPIServer(("localhost", 8080), MyRequestHandler, self)
        logger.info(f"Local server started at {REDIRECT_URL}")
        server.handle_request()

    def refresh_access_token(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
           'grant_type': 'refresh_token',
           'refresh_token': f'{self.refresh_token}',
        }
        res = requests.post(TOKEN_ENDPOINT, headers=headers, data=data)

        res.raise_for_status()
        token = res.json()

        # TODO: Can expires change ?
        self.ttl_cache['access_token'] = res['access_token']
        self.refresh_token = token['refresh_token']

        return res['access_token']

    def get_access_token(self, auth_code=None):
        if 'access_token' in self.ttl_cache:
            logger.info('Return access token from cache')
            return self.ttl_cache['access_token']

        if self.refresh_token:
            logger.info('Refreshing access token')
            access_token = self.refresh_access_token()
            return access_token
        
        logger.info('Authorizing with auth code.')
        if not auth_code:
            logger.error('No auth_code, impossible to authorize.')
            return None

        token_data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': REDIRECT_URL,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        response = requests.post(TOKEN_ENDPOINT, data=token_data)
        response.raise_for_status()

        if response.status_code == 200:
            token_info = response.json()
            self.ttl_cache['access_token'] = token_info['access_token']
            self.refresh_token = token_info['refresh_token']
            #logger.info("%s", token_info)
            return token_info
        
        logger.info(f"Error getting access token: %s", response.status_code)
        return None

    def get_token(self):
        # Client credentials, less privileged, currently not in use
        auth_str = self.client_id + ':' + self.client_secret
        auth_bytes = auth_str.encode('utf-8')
        auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')
        headers = {
            'Authorization': f"Basic {auth_base64}",
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'client_credentials'
        }
        res = requests.post(TOKEN_ENDPOINT, headers=headers, data=data)
        res.raise_for_status()
        self.auth_token = f"Bearer {res.json().get('access_token')}"
        return self.auth_token

    def get_current_user(self):
        url = f'{API_BASE_URL}/me'
        res = self._get_request(url)
        return res

    def get_user_playlists(self, user_id):
        url = f'{API_BASE_URL}/users/{user_id}/playlists'
        result = self._get_request(url)
        return result

    def get_playlist(self, playlist_id):
        url = f'{API_BASE_URL}/playlists/{playlist_id}'
        result = self._get_request(url)
        return result

    def get_track_audio_analysis(self, track_id):
        url = f'{API_BASE_URL}/audio-analysis/{track_id}'
        result = self._get_request(url)
        return result


class SpotifyAPIServer(socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, spotify_api):
        super().__init__(server_address, RequestHandlerClass)
        self.spotify_api = spotify_api


class MyRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract the authorization code from the callback URL
        query_components = parse_qs(urlparse(self.path).query)
        auth_code = query_components.get('code', [''])[0]

        self.server.spotify_api._auth_code = auth_code

        # Respond with a simple HTML message
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Authorization successful</h1></body></html>")

    def log_message(self, format, *args):
        pass


def main():
    myapi = SpoPyAPI()
    user = myapi.get_current_user()
    print(user)
    user_id = user.get('id')
    playlists = myapi.get_user_playlists(user_id)
    for playlist in playlists['items']:
        print(playlist['name'])
    
    technostick_id = [x['id'] for x in playlists['items'] if x['name'] == 'TeknoTikku'][0]
    techno = myapi.get_playlist(technostick_id)
    for row in techno['tracks']['items']:
        print(row['track']['name'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    load_dotenv('./spopyapi/secrets.env')

    main()
