import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

"""
Simple script to convert wav/mp4 to mp3 using ffmpeg
"""

OUT_FORMAT = 'mp3'
IN_FORMATS = [
    '.mp4',
    '.wav'
]

def main():

    in_path = Path(r'./music')
    out_path = in_path / OUT_FORMAT
    out_path.mkdir(exist_ok=False)

    for file in in_path.iterdir():
        if not file.is_file():
            logger.info('Skip non-files')
            continue
        
        if file.suffix not in IN_FORMATS:
            logger.info('Incorrect file format: %s', file)
            continue
        
        file_name = file.with_suffix(f'.{OUT_FORMAT}').name
        out_file = out_path / file_name
        cmd = f'ffmpeg -i \"{file}\" -vn \"{out_file}\"'
        os.system(cmd)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    main()
