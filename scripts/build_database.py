import mutagen
import os
import sys


sys.path.append("/stringwave/scripts")
from clean_radio import clean_track
from webapp import (
    app,
    db,
    Tracks,
    Config,
    create_admin_user,
    sw_logger as logger,
    flask_bcrypt,
)


stations = sys.argv[1:]
radio_path = f"{os.getcwd()}/radio/"
track_id = 1

for station in stations:
    # clear track list when going to the next station
    tracks = []

    logger.info(f"Building {station} tracks database...")
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
            logger.error(f"ERROR: {file_name} returned None")
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
            logger.error(f"KEY ERROR on {file_path}")
            continue

        track_id += 1

    with app.app_context():
        # create the stringwave database. this script is called before the app is run
        # the startup script drops the track database so you must create the tables before attempting to add tracks
        # create the discogs database and admin user as well
        db.create_all("main")
        db.create_all("discogs")
        create_admin_user(flask_bcrypt)

        # add config 0 for any tracks that have a config id not in the config table
        # or tracks added by pipefeeder
        db.session.add(
            Config(
                config_id=0,
                genres="",
                styles="",
                decade="",
                year="",
                country="",
                sort_method="",
                sort_order="",
                albums_to_find=0,
                is_active=False,
            )
        )

        # get list of Track objects
        track_objects = []
        for track in tracks:
            # set config to 0 if the config id doesn't exist in the config table
            config_exists = db.session.get(Config, config)
            if not config_exists:
                config = 0
            track_objects.append(
                Tracks(
                    track_id=track[0],
                    title=track[1],
                    artist=track[2],
                    track_type=track[3],
                    config=track[4],
                    station=track[5],
                    file_path=track[6],
                    discogs_link=track[7],
                )
            )
        logger.debug(f"Attempting to build {station} tracks database...")
        try:
            db.session.add_all(track_objects)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            logger.error(f"Failed to create {station} tracks database.)")
    logger.info(f"Done building {station} tracks database!")
