from cogmera import *
from webapp import *
import os
import sqlite3

con = sqlite3.connect('webapp/instance/configs.db')
cur = con.cursor()

configs = cur.execute('SELECT * FROM config ORDER BY RANDOM() LIMIT 5')

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

	downloadSongs(getAlbumData(buildUrl(
                                  setGenres(*config[1].split(';')),
                                  setStyles(*config[2].split(';')),
                                  setTime(config[3], config[4]),
                                  setSortMethod(config[6], config[7]),
                                  setCountry(config[5])), config[8], 5), config[8], str(config[0])) # param between config[8]s is num of pages to scrape, last param is config stamp
							
print('Done!')	
