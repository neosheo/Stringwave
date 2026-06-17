import mutagen
import os
import sys
import sqlite3

sys.path.append("/stringwave/scripts")
from clean_radio import clean_track
from webapp import app, db, Tracks


stations = sys.argv[1:]
radio_path = f"{os.getcwd()}/radio/"

for station in stations:
    # reset these when going to the next station
    track_id = 1
    tracks = []

    print(f"Building {station} tracks database...")
    for file_name in os.listdir(f"radio/{station}"):
        # makes sure file is safe to enter into database and radio
        file_name = clean_track(station, file_name)

        # skip the rest of the function if clean_track returned nothing (unsafe file was deleted)
        if not file_name:
            continue

        # write full file path which will be written into the database
        file_path = f"{radio_path}{station}/{file_name}"
        track = mutagen.File(file_path)

        # skip file if mutagen.File failed
        if not track:
            print(f"ERROR: {file_name} returned None")
            continue

        # pipefeeder doesn't add a config tag to the file, if these lines aren't included you get a KeyError
        if "config" not in track:
            track["config"] = 0

        # placeholder if track_type isn't present
        if "track_type" not in track:
            track["track_type"] = "n"

        # to prevent crash if a track has no discogs link
        if "discogs_link" not in track:
            track["discogs_link"] = "NA"

        try:
            tracks.append(
                (
                    track_id,
                    track["title"][0],
                    track["artist"][0],
                    track["track_type"][0],
                    track["config"][0],
                    station,
                    file_path,
                    track["discogs_link"][0],
                )
            )
        except KeyError:
            print(f"KEY ERROR on {file_path}")
            continue

        track_id += 1
    # station_tracks.append(tracks)

    # con = sqlite3.connect("webapp/instance/stringwave.db")
    # cur = con.cursor()
    with app.app_context():
        # create the stringwave database. this script is called before the app is run
        # the startup script drops the track database so you must create the tables before attempting to add tracks
        db.create_all("main")
        with db.session.begin():
            # get list of Track objects
            track_objects = []
            for track in tracks:
                track_objects.append(
                    track_id=track[0],
                    title=track[1],
                    artist=track[2],
                    track_type=track[3],
                    config=track[4],
                    station=track[5],
                    file_path=track[6],
                    discogs_link=track[7],
                )
            db.session.add_all(track_objects)
        # cur.executemany(
        #     "INSERT OR IGNORE INTO tracks(track_id, title, artist, track_type, config, station, file_path, discogs_link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        #     tracks,
        # )
        # con.commit()
    print("Done!")
