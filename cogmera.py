from webapp import *
from flask import redirect
import requests
from bs4 import BeautifulSoup
import subprocess 
import random
import os
import json
import sqlite3
import re
import time


class Album:
    def __init__(self, title, artist, link, tracklist, tracklist_artists):
        self.title = title
        self.artist = artist
        self.link = link
        self.tracklist = tracklist
        if tracklist_artists == []:
            self.tracklist_artists = None
        else:
            self.tracklist_artists = tracklist_artists
    def getRandomTrack(self):
        while True:
            random_number = random.randrange(len(self.tracklist))
            if self.tracklist[random_number] != '?':
                break
        return [self.tracklist[random_number], random_number]


def setGenres(*genres):
    if genres[0] == 'None':
        return ''
    genre_param = ''.join([f"&genre_exact={genre.title().replace(' ', '%20')}" for genre in genres])
    return genre_param


def setStyles(*styles):
	if styles[0] == 'None':
		return ''
	style_param = ''.join([f"&style_exact={style.title().replace(' ', '%20')}" for style in styles])
	return style_param


def setTime(decade='None', year='None'):
    if decade != 'None':
        decade_param = f"&decade={decade}"
    else:
        decade_param = ''
    if year != 'None':
        year_param = f"&year={year}"
    else:
        year_param = ''
    return f"{decade_param}{year_param}"


def setSortMethod(method, order):
    if order == 'D':
        order = 'desc'
    elif order == 'A':
        order = 'asc'
    else:
        print('Invalid sort order.')
    sort_param = f"sort={method}%2C{order}&"
    return sort_param


def setCountry(country='None'):
    if country != 'None':
        country_param = f"&country_exact={country}"
        return country_param
    return ''


def buildUrl(genre_param, style_param, time_param, sort_param, country_param, query=None):
    if query == None:
        url = f"https://www.discogs.com/search/?{sort_param}ev=em_rs{genre_param}{style_param}{time_param}{country_param}"
    else:
        url = f"https://www.discogs.com/search/?{sort_param}q={query}{genre_param}{style_param}{time_param}{country_param}"
    print(f'Search URL: {url}')
    return url


def selectRandomAlbums(albums, num_albums_to_pick):
    i = 0
    albums_selected = []
	# this list is to make sure duplicate albums are not selected
    albums_selected_titles = []
    while i < num_albums_to_pick:
        try:
            selected_album = random.randrange(len(albums))
        # force retry if it encounters a ValueError to prevent the program from exiting
        except ValueError:
            continue
        # check the selected album against a list of previously selected albums to skip duplicates
        if albums[selected_album][0].lower() in albums_selected_titles:
            continue
        albums_selected.append(albums[selected_album])
        albums_selected_titles.append(albums[selected_album][0].lower())
        i += 1
    return albums_selected


def getAlbumData(url, num_albums_to_pick, num_pages):
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'}
    tracklists = []
	# used to track the artists on albums with various artists
    titles, artists, links, albums, tracklist_artists = [], [], [], [], []
    for page in range(1, num_pages + 1):
        i = 0
        while True:
            # prevents application exiting on a failed connection
            if i == 5:
                return None
            try:
                html = requests.get(f'{url}&page={page}', headers=header).text
            except requests.exceptions.ConnectionError:
                continue
                i += 1
            break
        soup = BeautifulSoup(html, 'html.parser')
        # write titles, artists, and album links of selection to a list
        [titles.append(title.text) for title in soup.find_all('a', class_='search_result_title')]
        [artists.append(artist.text.strip().replace('\n', '')) for artist in soup.find_all('div', class_='card-artist-name')]
        [links.append(f"https://www.discogs.com{title['href']}") for title in soup.find_all('a', class_='search_result_title')]
        i = 0
        # combine them all into a list of "albums"
        for title in titles:
            albums.append((title, artists[i], links[i]))
            i += 1
    selected_albums = selectRandomAlbums(albums, num_albums_to_pick * 2)
    albums.clear()
    titles.clear()
    artists.clear()
    links.clear()
    for selected_album in selected_albums:
        # make a new list of titles, artists, and links for selections only
        titles.append(selected_album[0])
        artists.append(selected_album[1])
        links.append(selected_album[2])
    # select the random track
    for link in links:
        tracks = []
        track_artists = []
        html = requests.get(link, headers=header).text
        soup = BeautifulSoup(html, 'html.parser')
		# the first if statement is to fill in the artists of each track on albums with various artists
		# there are at least 2 different classes for tracks so the script will try both
        if soup.find('a', class_='link_1ctor link_15cpV').text == 'Various':
            # if the first occurenence of the artist element is 'Various', add the remaining artist elements to list
            for track_artist in soup.find_all('a', class_='link_1ctor link_15cpV')[1:]:
                track_artists.append(track_artist.text)
            # write all title elements to list, checking both potential classes
            if soup.find_all('span', class_='trackTitle_CTKp4') == []:
                for track in soup.find_all('td', class_='trackTitleNoArtist_ANE8Q'):
                    tracks.append(track.text)
            else:
                for track in soup.find_all('span', class_='trackTitle_CTKp4'):
                    tracks.append(track.text)
        # get data for albums that don't have Various
        else:
            if soup.find_all('span', class_='trackTitle_CTKp4') == []:
                for track in soup.find_all('td', class_='trackTitleNoArtist_ANE8Q'):
                    tracks.append(track.text)
            else:
                for track in soup.find_all('span', class_='trackTitle_CTKp4'):
                    tracks.append(track.text)
        tracklists.append(tracks)
        tracklist_artists.append(track_artists)
	# build the album object by grabbing the title and noting the index, then apply that index to the other lists
    for i, title in enumerate(titles):
        albums.append(Album(title, artists[i], links[i], tracklists[i], tracklist_artists[i]))
#    [print(f'Album selected: {album.title} - {album.artist}') for album in albums]
    return albums


def validateAlbums(albums, num_albums_to_pick):
	# this function is here to make sure albums return a tracklist
    # and that albums with various artists return track artists with same amount of tracks and track artists
    valid_albums = []
    i = 0
    for album in albums:
        if i == num_albums_to_pick:
            break
        if album.tracklist == []:
            print(f'EMPTY TRACKLIST: {album.link}')
            continue
        else:
            if album.tracklist_artists != None:
                if len(album.tracklist_artists) != len(album.tracklist):
                    continue    
            valid_albums.append(album)
            i += 1
    return valid_albums


# two parameters default to None to prevent the program from exiting if getAlbumDate returns None
def downloadSongs(albums, num_albums_to_pick=None, config_stamp=None):
    open('dl_data/search_queries', 'w').close()
    if albums == None:
        return 'No album found. Timed out.'
    albums = validateAlbums(albums, num_albums_to_pick)
    [print(f'Album selected: {album.title} - {album.artist}\nDiscogs link: {album.link}') for album in albums]
    for album in albums:
        random_track, random_number = album.getRandomTrack()
        if album.tracklist_artists != None:
            selected_artist = album.tracklist_artists[random_number]
        else:
            selected_artist = album.artist
        print(f'Track selected: {random_track} - {selected_artist}\n')
        random_track = re.sub(r'(\*|/)', '', random_track)
        selected_artist = re.sub(r'(\*|/)', '', selected_artist)
        data = {
            'filename': random_track,
            'artist': selected_artist,
            'search_query': f'{selected_artist} {random_track}',
            'config': config_stamp
        }
        with open('dl_data/search_queries', 'a') as f:
            json.dump(data, f, indent=4)
        requests.get('http://gateway:80/download/cogmera')


            #print(f'Track selected: {random_track} - {album.tracklist_artists[random_number]}\n')
            #headers = {"Content-Type": "application/json"}
            #post_data = {
                # 'app': 'cogmera',
                #'filename': random_track,
                #'artist': album.tracklist_artists[random_number],
                #'search_query': f'{album.tracklist_artists[random_number].replace("*", "").replace("/", "")} {random_track.replace("*", "").replace("/", "")}"',
                #'config': config_stamp
            #}
            #requests.post('http://gateway:80/download', headers=headers, json=post_data)
        #else:
            #print(f'Track selected: {random_track} - {album.artist}\n')
            #headers = {"Content-Type": "application/json"}
            #post_data = {
                # 'app': 'cogmera',
                #'filename': random_track,
                #'artist': album.artist,
                #'search_query': f'{album.artist.replace("*", "").replace("/", "")} {random_track.replace("*", "").replace("/", "")}"',
                #'config': config_stamp
            #}

            #requests.post('http://gateway:80/download', headers=headers, json=post_data)


def run_cogmera():
    con = sqlite3.connect('webapp/instance/stringwave.db')
    cur = con.cursor()

    configs = cur.execute(f'SELECT * FROM config ORDER BY RANDOM() LIMIT {os.getenv("NUM_DAILY_DOWNLOADS")}')


    for config in configs.fetchall():
        print(f'ID: {config[0]}')
        print(f'Genres: {config[1].replace(";", ", ")}')
        print(f'Styles: {config[2].replace(";", ", ")}')
        print(f'Decade: {config[3]}')
        print(f'Year: {config[4]}')
        print(f'Country: {config[5]}')
        print(f'Sort Method: {config[6]}')
        print(f'Sort Order: {config[7]}')
        print(f'Albums to Find: {config[8]}')

        config_stamp = config[0]
        genres = setGenres(*config[1].split(';'))
        styles = setStyles(*config[2].split(';'))
        time_param = setTime(config[3], config[4])
        sort_method = setSortMethod(config[6], config[7])
        country = setCountry(config[5])
        num_albums_to_scrape = config[8]
        num_daily_downloads = int(os.getenv('NUM_DAILY_DOWNLOADS'))
        url = buildUrl(genres,
                        styles,
                        time_param,
                        sort_method,
                        country)
        albums = getAlbumData(url, num_albums_to_scrape, num_daily_downloads)
        downloadSongs(albums, num_albums_to_scrape, str(config_stamp))

    #requests.get('http://gateway:80/check_download_completion/cogmera')
    time.sleep(300)
    requests.get('http://gateway:80/reread')

    print('Done!')	
    # return redirect('/download/cogmera')


if __name__ == '__main__':
    run_cogmera()