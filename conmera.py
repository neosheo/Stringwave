import os
import subprocess
from dotenv import load_dotenv

# initialize icecast
load_dotenv()
ic_username = os.getenv('ICECAST_USERNAME')
ic_password = os.getenv('ICECAST_PASSWORD')
ic_host = os.getenv('ICECAST_HOST')
ic_port = os.getenv('ICECAST_PORT')
ic_mountpoint = os.getenv('ICECAST_MOUNTPOINT')
ic_uri = f'icecast://{ic_username}:{ic_password}@{ic_host}:{ic_port}/{ic_mountpoint}'

# initialize paths
pool = f'{os.getcwd()}/Pool/'
pool_tracks = os.listdir(pool)
radio = f'{os.getcwd()}/Radio/'
radio_tracks = os.listdir(radio)


def remove_white_spaces_in_track_filenames():
    for old_file_name in pool_tracks:
        new_file_name = old_file_name.replace(' ', '_')
        os.rename(f'{pool}/{old_file_name}', f'{pool}/{new_file_name}')


def link_tracks():
    for index, track in enumerate(pool_tracks):
        subprocess.run(['ln', '-s', f'{pool}/{track}', f'{radio}/Track{index}.mp3'])


def start_radio():
    subprocess.run(['ffmpeg', '-re', '-stream_loop', '-1', '-f', 'concat', '-safe', '0', '-i', f'{radio}playlist.txt', '-c', 'copy', '-f', 'mp3', ic_uri ])


if __name__ == '__main__':
    remove_white_spaces_in_track_filenames()
    link_tracks()
    start_radio()