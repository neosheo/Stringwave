import os
import subprocess


pool = os.listdir(f'{os.getcwd()}/Pool/')
radio = os.listdir(f'{os.getcwd()}/Radio/')


def remove_white_spaces_in_track_filenames():
    for old_file_name in pool:
        new_file_name = old_file_name.replace(' ', '_')
        os.rename(f'{pool}/{old_file_name}', f'{pool}/{new_file_name}')


def relink_tracks():
    with open('Radio/playlist.txt') as f:
        tracks = f.readlines()
    for index, track in enumerate(tracks):
        subprocess.run(['ln', '-s', f'{pool}/{track}', f'{radio}/Track_{index}.mp3'])