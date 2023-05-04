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
main_radio = f'{os.getcwd()}/radio/main'
main_radio_tracks = os.listdir(main_radio)
new_radio = f'{os.getcwd()}/radio/new'
new_radio_tracks = os.listdir(new_radio)

# log paths
cogmera_log = f'{os.getcwd()}/logs/cogmera.log'
pipefeeder_log = f'{os.getcwd()}/logs/pipefeeder.log'


def remove_white_spaces_in_track_filenames(radio_dir):
    for old_file_name in radio_dir:
        new_file_name = old_file_name.replace(' ', '_')
        os.rename(f'{radio_dir}/{old_file_name}', f'{radio_dir}/{new_file_name}')


# def link_tracks(radio, radio_dir):
#     for index, track in enumerate(radio_dir):
#         subprocess.run(['ln', '-s', f'{radio_dir}/{track}', f'{radio}/Track{index}.mp3'])


# def start_radio():
#     subprocess.run(['ffmpeg', '-re', '-stream_loop', '-1', '-f', 'concat', '-safe', '0', '-i', f'{radio}playlist.txt', '-c', 'copy', '-f', 'mp3', ic_uri ])


if __name__ == '__main__':
    remove_white_spaces_in_track_filenames()
    #link_tracks()
    #start_radio()