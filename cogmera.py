import requests
from bs4 import BeautifulSoup
import random
import os
import json
import sqlite3
import re
import time
from webapp import app, db, Config, cm_logger as logger
from sqlalchemy import select, func


class Album:
    def __init__(self, title, artist, link, tracklist, tracklist_artists):
        self.title = title
        self.artist = artist
        self.link = link
        self.tracklist = tracklist
        # this is only for albums with multiple artists (i.e. compilation albums)
        if tracklist_artists == []:
            self.tracklist_artists = None
        else:
            self.tracklist_artists = tracklist_artists

    def get_random_track(self):
        while True:
            random_number = random.randrange(len(self.tracklist))
            # make sure randomly picked track doesn't return a "?"
            # if it does try again until it doesn't
            if self.tracklist[random_number] != "?":
                break
        return [self.tracklist[random_number], random_number]


def set_genres(*genres):
    if genres[0] == "None":
        logger.debug("No genres set")
        return ""

    # log genres passed to function
    for i, genre in enumerate(genres):
        logger.debug(f"Genre {i + 1} set to {genre}")

    genre_param = "".join(
        [f"&genre={genre.title().replace(' ', '%20')}" for genre in genres]
    )
    logger.debug(f"Genre parameter set as: {genre_param}")
    return genre_param


def set_styles(*styles):
    if styles[0] == "None":
        logger.debug("No styles set")
        return ""

    # log styles passed to function
    for i, style in enumerate(styles):
        logger.debug(f"STYLE {i + 1} SET TO {style}")

    style_list = []
    # alter URLs for styles with symbols or all capitals
    for style in styles:
        # encode "&s" that are part of the album title
        if "&" in style:
            style = style.replace("&", "%26")
        style_list.append(f"&style={style.replace(' ', '%20')}")
    style_param = "".join(style_list)
    style_param = f"""&{(
		style_param[1:].replace("/", "%2F")
		.replace("dj", "DJ")
		.replace("Uk", "UK")
		.replace("É", "%C3%89")
		.replace("ï", "%C3%AF")
		.replace("è", "%C3%A8")
		.replace("ō", "%C5%8D")
		.replace("ó", "%C3%B3")
		.replace("ó", "%C3%A9")
		.replace("ñ", "%C3%B1")
		.replace("é", "%C3%A9")
		.replace("ç", "%C3%A7")
		.replace("ã", "%C3%A3")
		.replace("ū", "%C5%AB")
		.replace("á", "%CC%81")
		.replace("č", "%C4%8D")
	)}"""
    logger.debug(f"Style parameter set to: {style_param}")
    return style_param


def set_time(decade="None", year="None"):
    if decade != "None":
        logger.debug(f"Decade set to {decade}")
        decade_param = f"&decade={decade}"
    else:
        logger.debug("No decade set")
        decade_param = ""
    if year != "None":
        logger.debug(f"Year set to {year}")
        year_param = f"&year={year}"
    else:
        logger.debug(f"No year set")
        year_param = ""
    logger.debug(f"Time parameter set to: {decade_param}{year_param}")
    return f"{decade_param}{year_param}"


def set_sort_method(method, order):
    logger.debug(f"Sort method set to {method}")
    logger.debug(f"Sort order set to {order}")
    if order == "D":
        order = "desc"
    elif order == "A":
        order = "asc"
    else:
        logger.error("Invalid sort order")
    sort_param = f"&sort={method}%2C{order}&"
    logger.debug(f"Sort parameter set to: {sort_param}")
    return sort_param


def set_country(country="None"):
    if country != "None":
        logger.debug(f"Country of origin set to {country}")
        country_param = f"&country={country}"
        logger.debug(f"Country of origin parameter set to: {country_param}")
        return country_param
    logger.debug(f"No country of origin set")
    return ""


def build_url(genre_param, style_param, time_param, sort_param, query=None):
    if query is None:
        url = f"https://api.discogs.com/database/search?per_page=100{genre_param}{style_param}{time_param}{sort_param}&token={os.getenv('DISCOGS_PERSONAL_ACCESS_TOKEN')}"
    else:
        url = f"https://api.discogs.com/database/search?per_page=100&q={query}{genre_param}{style_param}{time_param}{sort_param}&token={os.getenv('DISCOGS_PERSONAL_ACCESS_TOKEN')}"
    logger.debug(f"Search url: {url}")
    return url


def select_random_albums(albums, num_albums_to_pick):
    logger.debug(f"Albums passed to selection function: {albums}")
    logger.debug(f"Number of albums to pick: {num_albums_to_pick}")
    if len(albums) == 0:
        logger.error("No albums found")
        return "error: no albums"
    i = 0
    albums_selected = []
    # this list is to make sure duplicate albums are not selected
    albums_selected_titles = []
    # make sure num_albums_to_pick is of type int
    if type(num_albums_to_pick) == "str":
        num_albums_to_pick = int(num_albums_to_pick)
    while i < num_albums_to_pick:
        try:
            selected_album = random.choice(albums)
            logger.debug(f"Album selected: {selected_album[0]}")
        # force retry if it encounters a ValueError to prevent the program from exiting
        except ValueError:
            logger.error("ValueError on selection. Retrying...")
            continue
        # check the selected album against a list of previously selected albums to skip duplicates
        if selected_album[0].lower() in albums_selected_titles:
            logger.debug(
                f"{selected_album[0]} was already detected. Selecting another album..."
            )
            continue
        albums_selected.append(selected_album)
        albums_selected_titles.append(selected_album[0].lower())
        i += 1
    return albums_selected


def get_album_data(url, num_albums_to_pick, num_pages):
    logger.debug(f"Number of albums to pick: {num_albums_to_pick}")
    logger.debug(f"Number of pages to scrape: {num_pages}")
    header = {
        "User-Agent": "Cogmera/1.0",
    }
    tracklists = []
    # used to track the artists on albums with various artists
    titles, artists, links, albums, tracklist_artists = [], [], [], [], []
    for page in range(1, num_pages):
        logger.debug(f"Scraping page {page}...")
        i = 0
        while True:
            # prevents application exiting on a failed connection
            if i == 5:
                logger.error(f"{url} had too many connection errors. Giving up!")
                return None
            try:
                # load returned data as a json and only grab the results key
                search_results = json.loads(
                    requests.get(f"{url}&page={page}", headers=header).text
                )["results"]
                logger.debug(f"Scraped data for page {page}:\n{search_results}")
            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error on page {page}!")
                continue
                i += 1
            break
        [titles.append(album["title"].split(" - ")[1]) for album in search_results]
        [artists.append(album["title"].split(" - ")[0]) for album in search_results]
        [links.append(album["resource_url"]) for album in search_results]
        i = 0
        # combine them all into a list of "albums"
        for title in titles:
            albums.append((title, artists[i], links[i]))
            logger.debug(
                f"\nAlbum data:\nTitle: {title}\nArtist: {artists[i]}\nLink: {links[i]}"
            )
            i += 1
    logger.debug(f"Number of albums found: {len(albums)}")
    logger.debug("Selecting random albums...")
    # multiple number of albums to pick by 2 to have a backup pick for each slot
    selected_albums = select_random_albums(albums, num_albums_to_pick * 2)
    if selected_albums == "error: no albums":
        logger.error("No albums were found.")
        return
    logger.debug(f"SELECTED {len(selected_albums)} ALBUMS")
    albums.clear()
    titles.clear()
    artists.clear()
    links.clear()
    logger.debug("\nSelected albums:")
    for selected_album in selected_albums:
        logger.debug(f"{selected_album[0]} - {selected_album[1]}")
        # make a new list of titles, artists, and links for selections only
        titles.append(selected_album[0])
        artists.append(selected_album[1])
        links.append(selected_album[2])
    # select the random track
    # use index so you can check if album has various artists
    for i, link in enumerate(links):
        logger.debug(f"Getting tracklist from {link}")
        logger.debug(f"Artist of selected album is {artists[i]}")
        tracks = []
        track_artists = []
        album_data_text = requests.get(link, headers=header).text
        if not album_data_text:
            logger.debug("Album data returned a blank string")
        album_data = json.loads(album_data_text)
        tracklist = album_data["tracklist"]
        logger.debug(f"Number of tracks found: {len(tracklist)}")
        if len(album_data["artists"]) > 1:
            logger.debug("This album has multiple artists")
            for track in tracklist:
                logger.debug(f"Track found: {track['title']}")
                logger.debug(f"Track data: {track}")
                tracks.append(track["title"])
            artists = []
            for artist in album_data["artists"]:
                artists.append(artist["name"])
                if len(artists) == 1:
                    artist = artists[0]
                # if 2 artists, separate them with the word and
                elif len(artists) == 2:
                    artist = " and ".join(artists)
                # if more than 2 artists, separate them with commas and the word and before the last one
                elif len(artists) > 2:
                    artist = f'{", ".join(artists[:-1])}, and {artists[-1]}'
                logger.debug(f"Artist found: {artist}")
                track_artists.append(artist)
            pass
        else:
            logger.debug("This album does not have various artists")
            for track in tracklist:
                logger.debug(f"Track found: {track['title']}")
                tracks.append(track["title"])

        tracklists.append(tracks)
        logger.debug(f"This album has {len(tracklist)} tracks")
        tracklist_artists.append(track_artists)
        logger.debug(f"This album has {len(tracklist_artists)} artists")
        if len(tracklist_artists) > 1:
            logger.debug(tracklist_artists)
    # build the album object by grabbing the title and noting the index, then apply that index to the other lists
    for i, title in enumerate(titles):
        albums.append(
            Album(title, artists[i], links[i], tracklists[i], tracklist_artists[i])
        )
        [
            logger.debug(f"Album selected for download: {album.title} - {album.artist}")
            for album in albums
        ]
    return albums


def validate_albums(albums, num_albums_to_pick):
    # this function is here to make sure albums return a tracklist
    # and that albums with various artists return track artists with same amount of tracks and track artists
    valid_albums = []
    i = 0
    for album in albums:
        if i == num_albums_to_pick:
            logger.debug("validation complete")
            break
        if album.tracklist == []:
            logger.debug(f"Empty tracklist: {album.link}")
            continue
        else:
            if album.tracklist_artists is not None:
                if len(album.tracklist_artists) != len(album.tracklist):
                    logger.debug(
                        f"{album.title} has {len(album.tracklist_artists)} artists but {len(album.tracklist)} tracks"
                    )
                    continue
            logger.debug(f"{album.title} is a valid album")
            valid_albums.append(album)
            i += 1
    return valid_albums


# two parameters default to None to prevent the program from exiting if getAlbumDate returns None
def download_songs(albums, num_albums_to_pick=None, config_stamp=None):
    if albums == "error: no albums":
        logger.error("Can't download. No albums received.")
        return
    if albums is None:
        logger.error("Can't download. Timed out.")
        return "No album found. Timed out."
    albums = validate_albums(albums, num_albums_to_pick)
    [
        logger.info(
            f"Album selected: {album.title} - {album.artist}\nDiscogs link: {album.link}"
        )
        for album in albums
    ]
    for album in albums:
        random_track, random_number = album.get_random_track()
        logger.debug(f"Random track selected: {random_track}")
        logger.debug(f"Random track number: {random_number}")
        if album.tracklist_artists is not None:
            selected_artist = album.tracklist_artists[random_number]
        else:
            selected_artist = album.artist
        logger.debug(f"Random track artist: {selected_artist}")
        logger.info(f"Track selected: {random_track} - {selected_artist}\n")
        random_track = re.sub(r"(\*|/)", "", random_track)
        logger.debug(f"Random track title updated: {random_track}")
        selected_artist = re.sub(r"(\*|/)", "", selected_artist)
        logger.debug(f"Random track artist updated: {selected_artist}")
        header = {
            "User-Agent": "Cogmera/1.0",
        }
        data = {
            "filename": random_track,
            "artist": selected_artist,
            "search_query": f"{selected_artist} {random_track}",
            "config": config_stamp,
            "discogs_link": json.loads(requests.get(album.link, headers=header).text)[
                "uri"
            ]
            .split("/")[-1]
            .split("-")[0]
            .replace("release", "master"),
        }
        logger.debug(f"Data to pass to api: {data}")
        with open("dl_data/search_queries", "a") as f:
            json.dump(data, f)
            f.write("\n")


def run_cogmera():
    # pick random configs
    num_daily_downloads = int(os.getenv("NUM_DAILY_DOWNLOADS"))
    logger.debug(f"Application is set to select {num_daily_downloads} configurations")
    with app.app_context():
        configs = db.session.scalars(
            select(Config).where(Config.config_id != 0).order_by(func.random()).limit(num_daily_downloads)
        ).all()

    # clear old search queries
    open("dl_data/search_queries", "w").close()

    for config in configs:
        logger.info(f"\nID: {config.config_id}")
        logger.info(f'Genres: {config.genres.replace(";", ", ")}')
        logger.info(f'Styles: {config.styles.replace(";", ", ")}')
        logger.info(f"Decade: {config.decade}")
        logger.info(f"Year: {config.year}")
        logger.info(f"Country: {config.country}")
        logger.info(f"Sort Method: {config.sort_method}")
        logger.info(f"Sort Order: {config.sort_order}")
        logger.info(f"Albums to Find: {config.albums_to_find}")

        config_stamp = config.config_id

        # build discogs search url
        genres = set_genres(*config.genres.split(";"))
        styles = set_styles(*config.styles.split(";"))
        time_param = set_time(config.decade, config.year)
        sort_method = set_sort_method(config.sort_method, config.sort_order)
        country = set_country(config.country)
        num_albums_to_scrape = config.albums_to_find
        url = build_url(genres, styles, time_param, sort_method, country)
        albums = get_album_data(url, num_albums_to_scrape, 2)
        download_songs(albums, num_albums_to_scrape, str(config_stamp))

    # initiate download and check status until all downloads complete
    requests.get("http://gateway:8080/download/cogmera")
    while True:
        status_file = "dl_data/cm_download_status"
        # create download status file if it doesn't exist
        if not os.path.isfile(status_file):
            open(status_file, "w").close()

        with open(status_file, "r") as f:
            if f.read().rstrip() == "Done":
                logger.info("Initiating ezstream reread.")
                requests.get("http://gateway:8080/reread")
                break
        time.sleep(5)
    open(status_file, "w").close()
    logger.info("Cogmera completed successfully!")


if __name__ == "__main__":
    run_cogmera()
