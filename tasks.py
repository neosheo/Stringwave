from webapp import celery_app, db, Tracks
from pipefeeder import populateDb
import requests
import os
import subprocess
import re
from pathlib import Path
import shutil
import json
from mutagen.oggopus import OggOpus
from webapp import radio_path


@celery_app.task
def move_track(track):
	if track[-5:] != '.opus':
		track = f'{track}.opus'
	subprocess.run(['mv', f'{radio_path}/new/{track}', f'{radio_path}/main/{track}'])
	requests.get('http://gateway:8080/reread/new')
	requests.get('http://gateway:8080/reread/main')
	requests.get('http://gateway:8080/move_complete')


@celery_app.task
def download_track(app):
	match app:
		case 'cogmera':
			with open('dl_data/search_queries', 'r') as f:
				data = json.load(f)
			filename = re.sub(r'(\||%|&|:|;|,|!|-|\*|#|\\|/|\[|\|"])', '', data['filename'])
			title = data['filename']
			artist = data['artist']
			search_query = data['search_query']
			config = data['config']
			file_path = f'{radio_path}/new/{title}.opus'
			subprocess.run([f'{os.getcwd()}/scripts/cogmera-download.sh', filename, title, artist, search_query, config])
			new_track = Tracks(title=filename, artist=artist, config=config, station='new', file_path=file_path)
			db.session.add(new_track)
			db.session.commit()

		case 'pipefeeder':
			with open('dl_data/urls', 'r') as f:
				lines = f.readlines()
				num_links = len(lines)
				downloads = 1
				links = []
				for line in lines:
					links.append((line.split(';')[0], line.split(';')[1]))
			if links == []: 
				print('No videos to download')
				return
			print('Cleaning broken downloads...')
			for file in os.listdir(f'{radio_path}/new'):
				# delete directories with files in them which are created by failed downloads
				if os.path.isdir(f'{radio_path}/new/{file}'):
					shutil.rmdir(f'{radio_path}/new/{file}')
			print('Done!')
			for line, link in enumerate(links):
				link = link[0].strip()
				artist = link[1].strip()
				regex = r'^(https?:\/\/)?(www\.)?youtube\.com\/(watch\?)?v(=|\/).{11}$'
				if not re.match(regex, link):
					print(f'Invalid YouTube link at line {line}: {link}.')
					continue
				print(f'Downloading {link}')
				subprocess.run([f'{os.getcwd()}/scripts/pipefeeder-download.sh', link])
				# add most recent track to radio database
				tracks = os.listdir(f'{radio_path}/new')
				# remove .playlist from list incase it somehow is most recently created file
				tracks.remove('.playlist')
				tracks_with_path = [ f'{radio_path}/new/{track}' for track in tracks ]
				for track in tracks_with_path:
					if '.opus' not in track:
						tracks_with_path.remove(track)
				latest_track = Path(max(tracks_with_path, key=os.path.getctime)).stem
				latest_track_formatted = re.sub(r'_+', ' ', latest_track)
				if latest_track_formatted in os.listdir():
					print(f'Match found: {latest_track_formatted}')
				file_path = f'{radio_path}/new/{latest_track}.opus'
				track = OggOpus(file_path)
				track['title'] = latest_track_formatted
				track['artist'] = artist
				print(f'Latest track: {latest_track_formatted}')
				new_track = Tracks(title=latest_track_formatted, artist=artist, config='pf', station='new', file_path=file_path)
				db.session.add(new_track)
				db.session.commit()
				if downloads == num_links:
					with open('dl_data/pf_download_status' 'w') as f:
						f.write('Done')
				else:
					downloads += 1


@celery_app.task
def upload(file_path):
	populateDb(file_path)
	requests.get('http://gateway/upload_complete')
