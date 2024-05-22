import requests
from bs4 import BeautifulSoup
import random
import os
import json
import sqlite3
import re
import time
from webapp import logger


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
        return ""
    genre_param = "".join(
        [f"&genre={genre.title().replace(' ', '%20')}" for genre in genres]
    )
    return genre_param


def set_styles(*styles):
    if styles[0] == "None":
        return ""
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
    return style_param


def set_time(decade="None", year="None"):
    if decade != "None":
        decade_param = f"&decade={decade}"
    else:
        decade_param = ""
    if year != "None":
        year_param = f"&year={year}"
    else:
        year_param = ""
    return f"{decade_param}{year_param}"


def set_sort_method(method, order):
    if order == "D":
        order = "desc"
    elif order == "A":
        order = "asc"
    else:
        logger.debug(f"SORT ORDER: {order}")
        logger.error("INVALID SORT ORDER")
    sort_param = f"sort={method}%2C{order}&"
    return sort_param


def set_country(country="None"):
    if country != "None":
        country_param = f"&country={country}"
        return country_param
    return ""


def build_url(
    genre_param, style_param, time_param, sort_param, query=None
):
    if query is None:
        #url = f"https://www.discogs.com/search/?{sort_param}ev=em_rs{genre_param}{style_param}{time_param}{country_param}"
        url = f"https://api.discogs.com/database/search?per_page=100{genre_param}{style_param}{time_param}{sort_param}&token={os.getenv('DISCOGS_PERSONAL_ACCESS_TOKEN')}"
    else:
        #url = f"https://www.discogs.com/search/?{sort_param}q={query}{genre_param}{style_param}{time_param}{country_param}"
        url = f"https://api.discogs.com/database/search?per_page=100&q={query}{genre_param}{style_param}{time_param}{sort_param}&token={os.getenv('DISCOGS_PERSONAL_ACCESS_TOKEN')}"
    logger.debug(f"SEARCH URL: {url}")
    return url


def select_random_albums(albums, num_albums_to_pick):
    logger.debug(f"ALBUMS PASSED TO SELECTION FUNCTION: {albums}")
    logger.debug(f"NUMBER OF ALBUMS TO PICK: {num_albums_to_pick}")
    if len(albums) == 0:
        logger.error("NO ALBUMS FOUND")
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
            logger.debug(f"ALBUM SELECTED: {selected_album[0]}")
        # force retry if it encounters a ValueError to prevent the program from exiting
        except ValueError:
            logger.error("ValueError on selection. Retrying...")
            continue
        # check the selected album against a list of previously selected albums to skip duplicates
        if selected_album[0].lower() in albums_selected_titles:
            logger.debug(f"{selected_album[0]} WAS ALREADY DETECTED. SELECTING ANOTHER ALBUM...")
            continue
        albums_selected.append(selected_album)
        albums_selected_titles.append(selected_album[0].lower())
        i += 1
    return albums_selected


def get_album_data(url, num_albums_to_pick, num_pages):
    logger.debug(f"NUMBER OF ALBUMS TO PICK: {num_albums_to_pick}")
    logger.debug(f"NUMBER OF PAGES TO SCRAPE: {num_pages}")
    header = {
        "User-Agent": "Cogmera/1.0",
    }
    tracklists = []
    # used to track the artists on albums with various artists
    titles, artists, links, albums, tracklist_artists = [], [], [], [], []
    for page in range(1, num_pages):
        logger.debug(f"SCRAPING PAGE {page}...")
        i = 0
        while True:
            # prevents application exiting on a failed connection
            if i == 5:
                logger.error(f"{url} had too many connection errors. Giving up!")
                return None
            try:
                # load returned data as a json and only grab the results key
                search_results = json.loads(requests.get(f"{url}&page={page}").text)["results"]
                logger.debug(f"SCRAPED DATA FOR PAGE {page}:\n{search_results}")
            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error on page {page}!")
                continue
                i += 1
            break
        [
            titles.append(album["title"].split(" - ")[1])
            for album in search_results
        ]
        [
            artists.append(album["title"].split(" - ")[0])
            for album in search_results
        ]
        [
            links.append(album["resource_url"])
            for album in search_results
        ]
        i = 0
        # combine them all into a list of "albums"
        for title in titles:
            albums.append((title, artists[i], links[i]))
            logger.debug(f"\nALBUM DATA:\nTITLE: {title}\nARTIST: {artists[i]}\nLINK: {links[i]}")
            i += 1
    logger.debug(f"NUMBER OF ALBUMS FOUND: {len(albums)}")
    logger.debug("SELECTING RANDOM ALBUMS...")
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
    logger.debug("\nSELECTED ALBUMS:")
    for selected_album in selected_albums:
        logger.debug(f"{selected_album[0]} - {selected_album[1]}")
        # make a new list of titles, artists, and links for selections only
        titles.append(selected_album[0])
        artists.append(selected_album[1])
        links.append(selected_album[2])
    # select the random track
    # use index so you can check if album has various artists
    for i, link in enumerate(links):
        logger.debug(f"GETTING TRACKLIST FROM {link}")
        logger.debug(f"ARTIST OF SELECTED ALBUM IS {artists[i]}")
        tracks = []
        track_artists = []
        album_data = json.loads(requests.get(link, headers=header).text)
        tracklist = album_data["tracklist"]
        logger.debug(f"NUMBER OF TRACKS FOUND: {len(tracklist)}")
        if len(album_data["artists"]) > 1:
            logger.debug("THIS ALBUM HAS MULTIPLE ARTISTS")
            for track in tracklist:
                logger.debug(f"TRACK FOUND: {track['title']}")
                logger.debug(f"TRACK DATA: {track}")
                tracks.append(track["title"])
            artists = []
            for artist in album_data['artists']:
                artists.append(artist['name'])
                if len(artists) == 1:
                    artist = artists[0]
                # if 2 artists, separate them with the word and
                elif len(artists) == 2:
                    artist = " and ".join(artists)
                # if more than 2 artists, separate them with commas and the word and before the last one
                elif len(artists) > 2:
                    artist = f'{", ".join(artists[:-1])}, and {artists[-1]}'
                logger.debug(f"ARTIST FOUND: {artist}")
                track_artists.append(artist)
            pass
        else:
            logger.debug("THIS ALBUM DOES NOT HAVE VARIOUS ARTISTS")
            for track in tracklist:
                logger.debug(f"TRACK FOUND: {track['title']}")
                tracks.append(track["title"])

        tracklists.append(tracks)
        logger.debug(f"THIS ALBUM HAS {len(tracklist)} TRACKS")
        tracklist_artists.append(track_artists)
        logger.debug(f"THIS ALBUM HAS {len(tracklist_artists)} ARTISTS")
        if len(tracklist_artists) > 1:
            logger.debug(tracklist_artists)
    # build the album object by grabbing the title and noting the index, then apply that index to the other lists
    for i, title in enumerate(titles):
        albums.append(
            Album(title, artists[i], links[i], tracklists[i], tracklist_artists[i])
        )
        [logger.debug(f'ALBUM SELECTED FOR DOWNLOAD: {album.title} - {album.artist}') for album in albums]
    return albums


def validate_albums(albums, num_albums_to_pick):
    # this function is here to make sure albums return a tracklist
    # and that albums with various artists return track artists with same amount of tracks and track artists
    valid_albums = []
    i = 0
    for album in albums:
        if i == num_albums_to_pick:
            logger.debug("VALIDATION COMPLETE")
            break
        if album.tracklist == []:
            logger.debug(f"EMPTY TRACKLIST: {album.link}")
            continue
        else:
            if album.tracklist_artists is not None:
                if len(album.tracklist_artists) != len(album.tracklist):
                    logger.debug(f"{album.title} HAS {len(album.tracklist_artists)} ARTISTS BUT {len(album.tracklist)} TRACKS")
                    continue
            logger.debug(f"{album.title} IS A VALID ALBUM")
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
        logger.debug(f"RANDOM TRACK SELECTED: {random_track}")
        logger.debug(f"RANDOM TRACK NUMBER: {random_number}")
        if album.tracklist_artists is not None:
            selected_artist = album.tracklist_artists[random_number]
        else:
            selected_artist = album.artist
        logger.debug(f"RANDOM TRACK ARTIST: {selected_artist}")
        logger.info(f"Track selected: {random_track} - {selected_artist}\n")
        print(f"Track selected: {random_track} - {selected_artist}\n")
        random_track = re.sub(r"(\*|/)", "", random_track)
        logger.debug(f"RANDOM TRACK TITLE UPDATED: {random_track}")
        selected_artist = re.sub(r"(\*|/)", "", selected_artist)
        logger.debug(f"RANDOM TRACK ARTIST UPDATED: {selected_artist}")
        data = {
            "filename": random_track,
            "artist": selected_artist,
            "search_query": f"{selected_artist} {random_track}",
            "config": config_stamp,
        }
        logger.debug(f"DATA TO PASS TO API: {data}")
        with open("dl_data/search_queries", "a") as f:
            json.dump(data, f)
            f.write("\n")


def run_cogmera():
    con = sqlite3.connect("webapp/instance/stringwave.db")
    cur = con.cursor()

    configs = cur.execute(
        f'SELECT * FROM config ORDER BY RANDOM() LIMIT {os.getenv("NUM_DAILY_DOWNLOADS")}'
    )

    # clear old search queries
    open("dl_data/search_queries", "w").close()

    for config in configs.fetchall():
        logger.info(f"\nID: {config[0]}")
        logger.info(f'Genres: {config[1].replace(";", ", ")}')
        logger.info(f'Styles: {config[2].replace(";", ", ")}')
        logger.info(f"Decade: {config[3]}")
        logger.info(f"Year: {config[4]}")
        logger.info(f"Country: {config[5]}")
        logger.info(f"Sort Method: {config[6]}")
        logger.info(f"Sort Order: {config[7]}")
        logger.info(f"Albums to Find: {config[8]}")

        config_stamp = config[0]
        genres = set_genres(*config[1].split(";"))
        styles = set_styles(*config[2].split(";"))
        time_param = set_time(config[3], config[4])
        sort_method = set_sort_method(config[6], config[7])
        country = set_country(config[5])
        num_albums_to_scrape = config[8]
        num_daily_downloads = int(os.getenv("NUM_DAILY_DOWNLOADS"))
        url = build_url(genres, styles, time_param, sort_method, country)
        albums = get_album_data(url, num_albums_to_scrape, 2)
        download_songs(albums, num_albums_to_scrape, str(config_stamp))

    # initiate download and check status until all downloads complete
    requests.get("http://gateway:8080/download/cogmera")
    while True:
        with open("dl_data/cm_download_status", "r") as f:
            if f.read().rstrip() == "Done":
                logger.info("Initiating ezstream reread.")
                requests.get("http://gateway:8080/reread")
                break
        time.sleep(5)
    open("dl_data/cm_download_status", "w").close()
    print("Done!", flush=True)


if __name__ == "__main__":
    run_cogmera()
