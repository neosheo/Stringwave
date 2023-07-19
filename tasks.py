from webapp import celery_app, db, Tracks, cogmera_log, pipefeeder_log
from pipefeeder import populateDb
import requests
import os
import subprocess
import re
from pathlib import Path
import shutil
import json


@celery_app.task
def move_track(track):
	if track[-5:] != '.opus':
		track = f'{track}.opus'
	subprocess.run(['mv', f'/stringwave/radio/new/{track}', f'/stringwave/radio/main/{track}'])
	requests.get('http://gateway:8080/reread/new')
	requests.get('http://gateway:8080/reread/main')
	requests.get('http://gateway:8080/move_complete')


@celery_app.task
def download_track(app):
	match app:
		case 'cogmera':
			with open('dl_data/search_queries', 'r') as f:
				data = json.load(f)
			filename = re.sub(r'(\||%|&|:|;|,|-|\*|#|\\|/|\[|\|"])', '', data['filename'])
			artist = data['artist']
			search_query = data['search_query']
			config = data['config']
			subprocess.run([f'{os.getcwd()}/scripts/cogmera-download.sh', filename, artist, search_query, config])
			new_track = Tracks(title=filename, artist=artist, config=config, station='new')
			db.session.add(new_track)
			db.session.commit()

		case 'pipefeeder':
			with open('dl_data/urls', 'r') as f:
				links = f.readlines()
			if links == []: 
				print('No videos to download')
				return
			print('Cleaning broken downloads...')
			for file in os.listdir('/stringwave/radio/new'):
				# delete directories with files in them which are created by failed downloads
				if os.path.isdir(f'/stringwave/radio/new/{file}'):
					shutil.rmdir(f'/stringwave/radio/new/{file}')
			print('Done!')
			for line, link in enumerate(links):
				link = link.strip()
				regex = r'^(https?:\/\/)?(www\.)?youtube\.com\/(watch\?)?v(=|\/).{11}$'
				if not re.match(regex, link):
					print(f'Invalid YouTube link at line {line}: {link}.')
					continue
				print(f'Downloading {link}')
				subprocess.run([f'{os.getcwd()}/scripts/pipefeeder-download.sh', link])
				# add most recent track to radio database
				tracks = os.listdir('/stringwave/radio/new')
				# remove .playlist from list incase it somehow is most recently created file
				for track in tracks:
					if track == '.playlist':
						del track
						continue
				tracks_with_path = [ f'/stringwave/radio/new/{track}' for track in tracks ]
				latest_track = Path(max(tracks_with_path, key=os.path.getctime)).stem
				print(f'Latest track: {latest_track}')
				new_track = Tracks(title=latest_track, config='pf', station='new')
				db.session.add(new_track)
				db.session.commit()


@celery_app.task
def upload(file_path):
	populateDb(file_path)
	requests.get('http://gateway/upload_complete')
