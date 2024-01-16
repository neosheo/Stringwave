from webapp import celery_app, db, Tracks
from pipefeeder import populate_database
from scripts.update_track_data import update_track_data
import requests
import os
import subprocess
import re
import shutil
import json
from webapp import radio_path


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
            # read search queries and set proper attributes for database entry and download script
            with open("dl_data/search_queries", "r") as f:
                data = [line.rstrip() for line in f.readlines()]
                # num_queries and downloads are needed 
                # so program knows when all downloads have completed
                num_queries = len(data)
                downloads = 1
                for datum in data:
                    query = json.loads(datum)
                    # remove illegal characters and spaces from filename
                    filename = re.sub(
                        r'(\||%|&|:|;|,|!|-|\*|#|\\|/|\[|\|"])', "", query["filename"]
                    ).replace(" ", "_")
                    title = query["filename"]
                    artist = query["artist"]
                    search_query = query["search_query"]
                    config = query["config"]
                    file_path = f'{radio_path}/new/{filename}.opus'
                    # initiate the download
                    print(f"Downloading {title}...")
                    subprocess.run(
                        [
                            f"{os.getcwd()}/scripts/cogmera-download.sh",
                            filename,
                            title,
                            artist,
                            search_query,
                            config,
                        ]
                    )
                    print("Done!")
                    # enter new track into database
                    print(f"Entering {title} into database...")
                    new_track = Tracks(
                        title=filename,
                        artist=artist,
                        config=config,
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
                        print("All downloads complete!")
                    else:
                        print(f"Download {downloads} of {num_queries} complete.")
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
                print("No videos to download")
                return
            print("Done!")
            print("Cleaning broken downloads...")
            for file in os.listdir(f"{radio_path}/new"):
                # don't include hidden files
                # but include files that start with more than one '.'
                regex = r'^\.[^\.].+'
                if re.match(regex, file):
                    continue
                # delete directories with files in them which are created by failed downloads
                if os.path.isdir(f"{radio_path}/new/{file}"):
                    shutil.rmtree(f"{radio_path}/new/{file}")
            print("Done!")
            for line, video_data in enumerate(links):
                # separate data from the links list
                link = video_data[0].strip()
                artist = video_data[1].strip()
                video_title = video_data[2].strip()
                # only download youtube videos
                # don't download shorts
                regex = r"^(https?:\/\/)?(www\.)?youtube\.com\/(watch\?)?v(=|\/).{11}$"
                if not re.match(regex, link):
                    print(f"Invalid YouTube link at line {line}: {link}.")
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
                # write download information to log
                with open("dl_data/pipefeeder.log", "a") as f:
                    f.write(f"\n{result.stderr.decode()}")
                # only add new database entry if download completed successfully
                if result.returncode == 0:
                    # make the file path prettier and change metadata
                    track = result.stdout.rstrip().decode()
                    file_path, title = update_track_data(track, artist, video_title)
                    new_track = Tracks(
                        title=title,
                        artist=artist,
                        config="pf",
                        station="new",
                        file_path=file_path,
                    )
                    db.session.add(new_track)
                    db.session.commit()
                    print(f"Added {file_path}")
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
