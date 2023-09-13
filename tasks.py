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
def move_track(track_id, old_file_path, new_file_path):
	subprocess.run(['mv', old_file_path, new_file_path])
	entry = db.session.query(Tracks).filter_by(track_id=track_id).one()
	entry.station = 'main'
	entry.file_path = new_file_path
	db.session.commit()
	requests.get('http://gateway:8080/reread/new')
	requests.get('http://gateway:8080/reread/main')
	requests.get('http://gateway:8080/move_complete')


@celery_app.task
def download_track(app):
	match app:
		case 'cogmera':
			with open('dl_data/search_queries', 'r') as f:
				data = [ line.rstrip() for line in f.readlines() ]
				num_queries = len(data)
				downloads = 1
				for datum in data:
					query = json.loads(datum)
					filename = re.sub(r'(\||%|&|:|;|,|!|-|\*|#|\\|/|\[|\|"])', '', query['filename'])
					title = query['filename']
					artist = query['artist']
					search_query = query['search_query']
					config = query['config']
					file_path = f'{radio_path}/new/{title.replace(" ", "_")}.opus'
					subprocess.run([f'{os.getcwd()}/scripts/cogmera-download.sh', filename, title, artist, search_query, config])
					new_track = Tracks(title=filename, artist=artist, config=config, station='new', file_path=file_path)
					db.session.add(new_track)
					db.session.commit()
					if downloads == num_queries:
						with open('dl_data/cm_download_status', 'w') as f:
							f.write('Done')
					else:
						downloads += 1

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
				# don't include hidden files
				regex = r'^\..+'
				if re.match(regex, file):
					continue
				# delete directories with files in them which are created by failed downloads
				if os.path.isdir(f'{radio_path}/new/{file}'):
					shutil.rmtree(f'{radio_path}/new/{file}')
			print('Done!')
			for line, link_and_artist in enumerate(links):
				link = link_and_artist[0].strip()
				artist = link_and_artist[1].strip()
				regex = r'^(https?:\/\/)?(www\.)?youtube\.com\/(watch\?)?v(=|\/).{11}$'
				if not re.match(regex, link):
					print(f'Invalid YouTube link at line {line}: {link}.')
					downloads += 1
					continue
				print(f'Downloading {link}')
				subprocess.run([f'{os.getcwd()}/scripts/pipefeeder-download.sh', link])
				# add most recent track to radio database
				tracks = os.listdir(f'{radio_path}/new')
				tracks_with_path = [ f'{radio_path}/new/{track}' for track in tracks ]
				for track in tracks_with_path:
				# remove hidden files from list incase one somehow is most recently created file
					regex = r'^\..+'
					if re.match(regex, track):
						tracks_with_path.remove(track)
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
				track.save()
				file_path = f'{radio_path}/new/{latest_track_formatted.replace(" ", "_")}.opus'
				print(f'Latest track: {latest_track_formatted}')
				new_track = Tracks(title=latest_track_formatted, artist=artist, config='pf', station='new', file_path=file_path)
				db.session.add(new_track)
				db.session.commit()
				if downloads == num_links:
					with open('dl_data/pf_download_status', 'w') as f:
						f.write('Done')
				else:
					downloads += 1


@celery_app.task
def upload(file_path):
	populateDb(file_path)
	requests.get('http://gateway/upload_complete')
