import logging
from pathlib import Path

import xml.etree.ElementTree as ET

logger = logging.getLogger(__file__)


def parse_tracklist(file_path: Path):
    logger.info('Reading file: %s', file_path)
    tree = ET.parse(file_path)
    root = tree.getroot()
    playlist_entries = root.findall(".//PLAYLIST/ENTRY")

    tracks = []
    for entry in playlist_entries:
        pk = entry.find("PRIMARYKEY")
        ext = entry.find("EXTENDEDDATA")

        if pk is None or ext is None:
            logger.info('No PRIMARYKEY <%s> or EXTENDEDDATA <%s>', pk, ext)
            continue

        full_path = pk.attrib.get("KEY", "")
        filename = Path(full_path.replace("/:","/")).stem
        artist, title = filename.split(" - ", 1) # assume that all files have name "<artist> - <title>"

        if not artist or not title:
            logger.info('No artist or title: %s - %s')
            continue

        start_time = int(ext.attrib.get("STARTTIME", 0))
        
        tracks.append({
            "start": start_time,
            "artist": artist,
            "title": title
        })
    return tracks


def main():
    """parse nml file and create formatted tracklist"""
    
    file_path = Path(r'tracklist\history_2025y11m06d_02h22m56s.nml')
    logger.info('Reading file: %s', file_path)
    
    tracklist = parse_tracklist(file_path)

    tracks_sorted = sorted(tracklist, key=lambda x: x["start"])

    start_time = tracklist[0]['start']

    for i, t in enumerate(tracks_sorted, 1):
        current_time = t['start'] - start_time
        current_minutes = int(current_time / 60)
        current_seconds = int(current_time % 60)
        time_str = f'{current_minutes}.{current_seconds}'
        print(f"{i:02d}. {time_str}: {t['artist']} - {t['title']}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
