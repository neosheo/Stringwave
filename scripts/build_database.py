import mutagen
import os
import sys
import sqlite3
import shutil
import re


stations = sys.argv
tracks = []
station_tracks = []
track_id = 1

for station in stations[1:]:
    for file in os.listdir(f'radio/{station}'):
        # this file may be present but shouldn't be added to the database
        if file == '.playlist':
            continue
        regex = r'.+\.part$'
        if re.match(regex, file):
            os.remove(f'radio/{station}/{file}')
            continue
        # sometimes downloads fail and create a directory with a file inside, this cleans them up
        if os.path.isdir(f'radio/{station}/{file}'):
            shutil.rmtree(f'radio/{station}/{file}')
            continue
        # remove non-breaking spaces from file names
        if u'\xa0' in file:
            new_name = file.replace(u'\xa0', '')
            os.rename(f'{os.getcwd()}/radio/{station}/{file}', f'{os.getcwd()}/radio/{station}/{new_name}')
            file = new_name
        track = mutagen.File(f'{os.getcwd()}/radio/{station}/{file}')
        # pipefeeder doesn't add a config tag to the file, if these lines aren't included you get a KeyError
        if 'config' not in track:
            track['config'] = 'na'
        tracks.append((track_id, track['title'][0], track['artist'][0], track['config'][0], station))
        track_id += 1
    station_tracks.append(tracks)
    
        
    con = sqlite3.connect('webapp/instance/stringwave.db')
    cur = con.cursor()
    for tracks in station_tracks:
        cur.executemany('INSERT OR IGNORE INTO tracks(track_id, title, artist, config, station) VALUES (?, ?, ?, ?, ?)', tracks)
    con.commit()
