import mutagen
import os
import sys
import sqlite3
sys.path.append("/stringwave/scripts")
from clean_radio import clean_track


stations = sys.argv
tracks = []
station_tracks = []
track_id = 1

for station in stations[1:]:
    print(f'Building {station} tracks database...')
    for file_name in os.listdir(f'radio/{station}'):
        file_name = clean_track(station, file_name)

        if file_name is None:
            continue
        file_path = f'/stringwave/radio/{station}/{file_name}'
        track = mutagen.File(f'{os.getcwd()}/radio/{station}/{file_name}')
        
        # pipefeeder doesn't add a config tag to the file, if these lines aren't included you get a KeyError
        if track is None:
            print(f'ERROR: {file_name}')
            continue
        
        if 'config' not in track:
            track['config'] = 0
        
        # placeholder if track_type isn't present
        if 'track_type' not in track:
            track['track_type'] = 'n'

        # to prevent crash if a track has no discogs link
        if 'discogs_link' not in track:
            track['discogs_link'] = 'NA'
        
        try:
            tracks.append((track_id,
                track['title'][0],
                track['artist'][0],
                track['track_type'][0],
                track['config'][0],
                station,
                file_path,
                track['discogs_link'][0]))
        except KeyError:
            print(f'KEY ERROR on {file_path}')
            continue
        
        track_id += 1
    station_tracks.append(tracks)
        
    con = sqlite3.connect('webapp/instance/stringwave.db')
    cur = con.cursor()
    for tracks in station_tracks:
        cur.executemany('INSERT OR IGNORE INTO tracks(track_id, title, artist, track_type, config, station, file_path, discogs_link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', tracks)
    con.commit()
    print('Done!')
