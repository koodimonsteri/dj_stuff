import logging
import os
from typing import Dict, List

if __name__ == '__main__':
    # Had some importing problemos when running this file,
    # Add parent directory to python path
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)

from dotenv import load_dotenv

from spopy.spopyapi import SpoPyAPI

logger = logging.getLogger(__name__)

class SpoPyClient:

    def __init__(self, client_id=None, client_secret=None):
        cl_id = client_id or os.getenv('SPOPY_CLIENT_ID')
        cl_secret = client_id or os.getenv('SPOPY_CLIENT_SECRET')
        self.api = SpoPyAPI(cl_id, cl_secret)
        self.current_user = self.api.get_current_user()

    def get_my_playlist_by_name(self, playlist_name: str) -> Dict:
        logger.info('Get current user playlist by name: %s', playlist_name)
        playlists = self.api.get_user_playlists(self.current_user.get('id'))
        playlist = [x for x in playlists['items'] if x.get('name') == playlist_name]
        if len(playlist) != 1:
            logger.error('Unable to find playlist. found playlists len(%s)', len(playlist))
            return {}
        return playlist[0]
    
    def get_playlist_tracks_by_name(self, playlist_name: str) -> List:
        playlist = self.get_my_playlist_by_name(playlist_name)
        if not playlist:
            return []
        playlist_tracks = self.api.get_playlist(playlist.get('id'))
        tracks = playlist_tracks.get('tracks', {}).get('items', [])
        return tracks


def main():
    my_client = SpoPyClient()
    
    for row in my_client.get_playlist_tracks_by_name('TeknoTikku'):
        print(row)
        exit(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    load_dotenv('./spopy/secrets.env')
    main()