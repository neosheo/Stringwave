import requests
from bs4 import BeautifulSoup
import subprocess 
import random
import os
import json


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
        selected_album = random.randrange(len(albums))
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
        html = requests.get(f'{url}&page={page}', headers=header).text
        soup = BeautifulSoup(html, 'html.parser')
        [titles.append(title.text) for title in soup.find_all('a', class_='search_result_title')]
        [artists.append(artist.text.strip().replace('\n', '')) for artist in soup.find_all('div', class_='card-artist-name')]
        [links.append(f"https://www.discogs.com{title['href']}") for title in soup.find_all('a', class_='search_result_title')]
        i = 0
        for title in titles:
            albums.append((title, artists[i], links[i]))
            i += 1
    selected_albums = selectRandomAlbums(albums, num_albums_to_pick * 2)
    albums.clear()
    titles.clear()
    artists.clear()
    links.clear()
    for selected_album in selected_albums:
        titles.append(selected_album[0])
        artists.append(selected_album[1])
        links.append(selected_album[2])
    for link in links:
        tracks = []
        track_artists = []
        html = requests.get(link, headers=header).text
        soup = BeautifulSoup(html, 'html.parser')
		# the first if statement is to fill in the artists of each track on albums with various artists
		# there are at least 2 different xpaths for tracks so the script will try both
        if soup.find('a', class_='link_1ctor link_15cpV').text == 'Various':
            for track_artist in soup.find_all('a', class_='link_1ctor link_15cpV')[1:]:
                track_artists.append(track_artist.text)
            if soup.find_all('span', class_='trackTitle_CTKp4') == []:
                for track in soup.find_all('td', class_='trackTitleNoArtist_ANE8Q'):
                    tracks.append(track.text)
            else:
                for track in soup.find_all('span', class_='trackTitle_CTKp4'):
                    tracks.append(track.text)
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


def downloadSongs(albums, num_albums_to_pick, config_stamp):
    albums = validateAlbums(albums, num_albums_to_pick)
    [print(f'Album selected: {album.title} - {album.artist}\nDiscogs link: {album.link}') for album in albums]
    for album in albums:
        random_track, random_number = album.getRandomTrack()
        if album.tracklist_artists != None:
            print(f'Track selected: {random_track} - {album.tracklist_artists[random_number]}')
            headers = {"Content-Type": "application/json"}
            post_data = {
                'app': 'cogmera',
                'filename': random_track,
                'artist': album.tracklist_artists[random_number],
                'search_query': f'{album.tracklist_artists[random_number].replace("*", "").replace("/", "")} {random_track.replace("*", "").replace("/", "")}"',
                'config': config_stamp
            }
            requests.post('http://gateway:80/download', json=post_data)
        else:
            print(f'Track selected: {random_track} - {album.artist}')
            headers = {"Content-Type": "application/json"}
            post_data = {
                'app': 'cogmera',
                'filename': random_track,
                'artist': album.artist,
                'search_query': f'{album.artist.replace("*", "").replace("/", "")} {random_track.replace("*", "").replace("/", "")}"',
                'config': config_stamp
            }
            requests.post('http://gateway:80/download', headers=headers, json=post_data)
