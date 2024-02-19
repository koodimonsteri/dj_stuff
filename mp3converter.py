from pathlib import Path
import os

"""
Simple script to convert wav to mp3 using ffmpeg
"""

def main():

    in_path = Path(r'./music')
    out_path = in_path / 'mp3'
    for file in in_path.iterdir():
        if not file.is_file():
            continue
        out_file = out_path / file.with_suffix('.mp3').name
        cmd = f'ffmpeg -i \"{file}\" -vn \"{out_file}\"'
        os.system(cmd)


if __name__ == '__main__':
    main()
