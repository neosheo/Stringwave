import mutagen
import os
import sys
import sqlite3

station = sys.argv[1]
tracks = []
track_id = 1

for file in os.listdir(f'radio/{station}'):
    if file == '.playlist':
        continue
    track = mutagen.File(f'{os.getcwd()}/radio/{station}/{file}')
    tracks.append((track_id, track['title'][0], track['artist'][0], track['config'][0]))
    track_id += 1

con = sqlite3.connect('webapp/instance/radio.db')
cur = con.cursor()
cur.executemany('INSERT OR IGNORE INTO tracks(track_id, filename, artist, config) VALUES (?, ?, ?, ?)', tracks)
con.commit()
