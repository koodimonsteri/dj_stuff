import logging
import os

import requests
from dotenv import load_dotenv

from credentials import Credentials

logger = logging.getLogger(__name__)


API_BASE_URL = 'https://api.spotify.com/v1'


class SpoPyAPI:
    """
    API implementation.
    only endpoints and request logics here
    Other logic goes to client.
    """
    def __init__(self, client_id=None, client_secret=None):
        cl_id = client_id or os.getenv('SPOPY_CLIENT_ID', None)
        cl_secret = client_secret or os.getenv('SPOPY_CLIENT_SECRET', None)
        self.credentials = Credentials(cl_id, cl_secret)

    def _get_request(self, url, params=None):
        logger.info('Get URL: %s', url)
        headers = {
            'Authorization': f'Bearer {self.credentials.get_access_token()}'
        }
        result = requests.get(url, headers=headers, params=params)
        result.raise_for_status()
        return result.json()

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

    def get_recently_played(self):
        url = f'{API_BASE_URL}/me/player/recently-played'
        result = self._get_request(url)
        return result

    def get_search(self, params=[]):
        url = f'{API_BASE_URL}/search'
        res = self._get_request(url, params=params)
        return res


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
