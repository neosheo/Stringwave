import mutagen
import os
import sys
import sqlite3
import shutil

station = sys.argv[1]
tracks = []
track_id = 1

for file in os.listdir(f'radio/{station}'):
    if file == '.playlist':
        continue
    if os.path.isdir(f'radio/{station}/{file}'):
        shutil.rmtree(f'radio/{station}/{file}')
        continue
    track = mutagen.File(f'{os.getcwd()}/radio/{station}/{file}')
    tracks.append((track_id, track['title'][0], track['artist'][0], track['config'][0], station))
    track_id += 1
        
con = sqlite3.connect('webapp/instance/radio.db')
cur = con.cursor()
cur.executemany('INSERT OR IGNORE INTO tracks(track_id, title, artist, config, station) VALUES (?, ?, ?, ?, ?)', tracks)
con.commit()
