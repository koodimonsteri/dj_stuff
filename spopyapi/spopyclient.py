import logging
import os

from dotenv import load_dotenv

from spopyapi import SpoPyAPI

logger = logging.getLogger(__name__)

class SpoPyClient:

    def __init__(self, client_id=None, client_secret=None):
        cl_id = client_id or os.getenv('SPOPY_CLIENT_ID')
        cl_secret = client_id or os.getenv('SPOPY_CLIENT_SECRET')
        self.api = SpoPyAPI(cl_id, cl_secret)
        self.current_user = self.api.get_current_user()

    def get_my_playlist_by_name(self, playlist_name: str):
        logger.info('Get current user playlist by name: %s', playlist_name)
        playlists = self.api.get_user_playlists(self.current_user.get('id'))
        playlist = [x for x in playlists['items'] if x.get('name') == playlist_name]
        if len(playlist) != 1:
            logger.error('Unable to find playlist. found playlists len(%s)', len(playlist))
            return []
        return playlist


def main():
    my_client = SpoPyClient()
    print(my_client.get_my_playlist_by_name('TeknoTikku'))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    load_dotenv('./spopyapi/secrets.env')
    main()