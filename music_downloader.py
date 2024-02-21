
import logging
import os
from re import search

from dotenv import load_dotenv
from pathlib import Path
from pytube import Search, YouTube

from spopy.spopyclient import SpoPyClient


logger = logging.getLogger(__name__)


OUT_PATH = Path(r'./music')


def search_from_youtube(search_str: str):
    """Returns first match"""
    logger.info('Searching video from youtube: %s', search_str)

    results = Search(search_str)
    if not results.results:
        logger.warning('Failed to find video!')
        return None
    
    video = results.results[0]
    #print(video)
    return video


def download_video(out_file_name, video_url):
    """ Download video and save it to OUT_PATH"""

    logger.info('Downloading video: %s', out_file_name)
    logger.info('URL: %s', video_url)

    try:
        yt = YouTube(video_url)
    except Exception as e:
        logger.error('Something happened when created YouTube object !\n%s', e)
        logger.debug(e)
        return None
    
    format = 'mp4'
    file_name = f'{out_file_name}.{format}'

    if (OUT_PATH / file_name).exists():
        logger.info('File already exists!')
        return OUT_PATH / file_name
    
    try:
        current_video = yt.streams.get_audio_only()
        logger.info('Current video: %s', current_video)

        current_video.download(output_path=str(OUT_PATH), filename=file_name)
    except Exception as e:
        logger.error('Something happened while downloading!')
        logger.exception(e)
        return None
    
    logger.info('Finished downloading, saved file to: %s', OUT_PATH / file_name)
    return OUT_PATH / file_name


def download_spotify_playlist(playlist_name: str):
    """
    Get all tracks in spotify playlist
    Search from youtube by track name and all artists
    Download and save by name: {main artist} - {track name}
    """
    logger.info('Dowloading spotify playlist: %s', playlist_name)
    downloaded_videos = []
    spopy_client = SpoPyClient()
    playlist_tracks = spopy_client.get_playlist_tracks_by_name(playlist_name)

    for track_item in playlist_tracks[:5]:
        track = track_item['track']
        track_name = track['name']
        main_artist = track['artists'][0]['name']
        artists = ' '.join([x['name'] for x in track['artists']])
        search_str = f'{track_name} {artists}'

        try:
            video = search_from_youtube(search_str)
        except Exception as e:
            logger.error('Failed to search from youtube')
            logger.debug(e)
            continue

        out_file_name = f'{main_artist} - {track_name}'
        if os.path.exists(OUT_PATH / f'{out_file_name}.mp4'):
            logger.info('Video has already been downloaded')
            continue
        
        file_path = download_video(out_file_name, video.watch_url)
        if file_path:
            downloaded_videos.append(file_path)

    logger.info('Finished downloading. Total downloaded videos: %s', len(downloaded_videos))
    return downloaded_videos


def main():

    logger.info('Downloading some spotify playlists')
    logger.info('from YouTube..')
    track_name = 'Airod - Ackerman'
    #video = search_from_youtube(track_name)
    #res = download_video(track_name, video.watch_url)

    downloaded_videos = download_spotify_playlist('TeknoTikku')
    
    #logger.info('Downloaded videos: %s', downloaded_videos)
    #logger.info('Total videos: %s', len(downloaded_videos))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    load_dotenv('./spopy/secrets.env')
    main()
