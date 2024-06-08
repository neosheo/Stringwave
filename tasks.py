from webapp import celery_app, db, Tracks, Subs, logger, radio_path
from disallowed_titles import disallowed_titles
from pipefeeder import populate_database
from scripts.update_track_data import update_track_data
import requests
import os
import subprocess
import re
import shutil
import json


@celery_app.task
def move_track(track_id, old_file_path, new_file_path):
    subprocess.run(["mv", old_file_path, new_file_path])
    entry = db.session.query(Tracks).filter_by(track_id=track_id).one()
    entry.station = "main"
    entry.file_path = new_file_path
    db.session.commit()
    requests.get("http://gateway:8080/reread/new")
    requests.get("http://gateway:8080/reread/main")
    requests.get("http://gateway:8080/move_complete")


@celery_app.task
def download_track(app):
    match app:
        case "cogmera":
            logger.debug("COGMERA INITIATED A DOWNLOAD")
            # read search queries and set proper attributes for database entry and download script
            with open("dl_data/search_queries", "r") as f:
                data = [line.rstrip() for line in f.readlines()]
                # num_queries and downloads are needed 
                # so program knows when all downloads have completed
                num_queries = len(data)
                logger.debug(f"RECEIVED {num_queries} SEARCH QUERIES")
                downloads = 1
                print("Starting cogmera downloads...")
                for datum in data:
                    query = json.loads(datum)
                    logger.debug(f"DATA RECEIVED: {query}")
                    # remove illegal characters and spaces from filename
                    filename = re.sub(
                        r'(\||%|&|:|;|,|!|-|\*|#|\\|/|\[|\|"])', "", query["filename"]
                    ).replace(" ", "_")
                    logger.debug(f"FILENAME: {filename}")
                    title = query["filename"]
                    logger.debug(f"TITLE: {title}")
                    # remove the (#) that are added by discogs for artists with the same name
                    artist = re.sub(
                        r"\s\(\d+\)", "", query["artist"]
                    ).rstrip()
                    logger.debug(f"ARTIST: {artist}")
                    search_query = query["search_query"]
                    logger.debug(f"SEARCH QUERY: {search_query}")
                    config = query["config"]
                    logger.debug(f"CONFIG: {config}")
                    file_path = f'{radio_path}/new/{filename}.opus'
                    logger.debug(f"FILE PATH: {file_path}")
                    # initiate the download
                    logger.info(f"Downloading {title}...")
                    result = subprocess.run(
                        [
                            f"{os.getcwd()}/scripts/cogmera-download.sh",
                            filename,
                            title,
                            artist,
                            search_query,
                            config,
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT
                    )
                    logger.debug(f"DOWNLOAD SCRIPT EXIT CODE: {result.returncode}")
                    logger.info(result.stdout.decode())
                    print("Done!")
                    # enter new track into database
                    logger.info(f"Entering {title} into database...")
                    print(f"Entering {title} into database...")
                    new_track = Tracks(
                        title=filename,
                        artist=artist,
                        track_type="c",
                        config=[config],
                        station="new",
                        file_path=file_path,
                    )
                    db.session.add(new_track)
                    db.session.commit()
                    print("Done!")
                    # increments downloads counter until
                    # downloads = number of queries
                    if downloads == num_queries:
                        with open("dl_data/cm_download_status", "w") as f:
                            f.write("Done")
                        logger.info("All downloads complete!")
                    else:
                        logger.info(f"Download {downloads} of {num_queries} complete.")
                        downloads += 1

        case "pipefeeder":
            print("Gathering links...")
            with open("dl_data/urls", "r") as f:
                lines = f.readlines()
                # downloads and num_links needed
                # to check when all downloads are complete
                num_links = len(lines)
                downloads = 1
                links = []
                # each "link" is in the format: <URL>;<artist>;<title>
                # create a list of tuples split by the semicolons
                for line in lines:
                    links.append((line.split(";")[0], line.split(";")[1], line.split(";")[2]))
            if links == []:
                logger.info("No videos to download")
                return
            print("Done!")
            print("Cleaning broken downloads...")
            for file in os.listdir(f"{radio_path}/new"):
                # don't include hidden files
                # but include files that start with more than one '.'
                regex = r'^\.[^\.].+'
                if re.match(regex, file):
                    logger.debug(f"SKIPPING HIDDEN FILE: {file}")
                    continue
                # delete directories with files in them which are created by failed downloads
                if os.path.isdir(f"{radio_path}/new/{file}"):
                    logger.debug(f"FAILED DOWNLOAD FOUND: {radio_path}/new/{file}")
                    shutil.rmtree(f"{radio_path}/new/{file}")
            print("Done!")
            for line, video_data in enumerate(links):
                # separate data from the links list
                link = video_data[0].strip()
                logger.debug(f"PARSED LINK FROM DOWNLOAD DATA: {link}")
                logger.debug(f"PARSED CHANNEL_ID FROM DOWNLOAD DATA: {video_data[1]}")
                artist = db.session.query(Subs).filter_by(channel_id=video_data[1].strip()).scalar().channel_name
                video_title = video_data[2].strip()
                logger.debug(f"PARSED ARTIST FROM DOWNLOAD DATA: {artist}")
                logger.debug(f"PARSED VIDEO TITLE FROM DOWNLOAD DATA: {video_title}")
                # only download youtube videos
                # don't download shorts
                regex = r"^(https?:\/\/)?(www\.)?youtube\.com\/(watch\?)?v(=|\/).{11}$"
                if not re.match(regex, link):
                    logger.debug(f"INVALID YOUTUBE LINK AT LINE {line}: {link}.")
                    # increment the download counter because the
                    # invalid link was included in the number of links
                    downloads += 1
                    continue
                # initiate download
                print(f"Downloading {link}")
                result = subprocess.run(
                    [f"{os.getcwd()}/scripts/pipefeeder-download.sh", link],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                logger.debug(f"DOWNLOAD SCRIPT EXIT CODE: {result.returncode}")
                logger.info(result.stderr.decode())
                # only add new database entry if download completed successfully
                if result.returncode == 0:
                    # make the file path prettier and change metadata
                    track_name = result.stdout.decode()
                    logger.debug(f"TRACK TITLE BEFORE UPDATING DATA: {track_name}")
                    file_path, title = update_track_data(track_name, artist, video_title)
                    logger.debug(f"DOWNLOADED TRACK: {title}")
                    logger.debug(f"DOWNLOADED FILE PATH: {file_path}")
                    title_is_allowed = [True]
                    for disallowed_title in disallowed_titles:
                        if re.match(title.rstrip(), disallowed_title):
                           logger.debug(f"DISALLOWED TITLE FOUND: {title}")
                           title_is_allowed[0] = False
                           break
                    if title_is_allowed[0]:
                        new_track = Tracks(
                            title=title,
                            artist=artist,
                            track_type="p",
                            config=[0],
                            station="new",
                            file_path=file_path,
                        )
                        db.session.add(new_track)
                        db.session.commit()
                        logger.debug(f"ADDED FILE {file_path} TO DATABASE")
                        logger.debug(f"TRACK TITLE: {title}")
                        logger.debug(f"ARTIST: {artist}")
                    # delete a file was not added to the database if it exists
                    # this will delete database entries for files skipped by download script's match filter
                    else:
                        if os.path.exists(file_path):
                            entry_to_delete = db.session.query(Tracks).filter_by(file_path=file_path).one()
                            logger.debug(f"DELETING DATABASE ENTRY FOR {title}. THIS ENTRY WAS BLOCKED BY THE DOWNLOAD SCRIPT")
                            db.session.delete(entry_to_delete)
                            db.session.commit()
                # increments downloads counter until
                # downloads = number of links
                if downloads == num_links:
                    with open("dl_data/pf_download_status", "w") as f:
                        f.write("Done")
                    print("All downloads complete!")
                else:
                    print(f"Download {downloads} of {num_links} complete.")
                    downloads += 1


@celery_app.task
# rebuilds database from a backup
def upload(file_path):
    populate_database(file_path)
    requests.get("http://gateway/upload_complete")
