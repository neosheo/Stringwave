from webapp import celery_app, db, Tracks
from pipefeeder import populateDb
from scripts.update_track_data import update_track_data
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
			print('Gathering links...')
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
			print('Done!')
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
				result = subprocess.run([f'{os.getcwd()}/scripts/pipefeeder-download.sh', link], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				# write download information to log
				with open('dl_data/pipefeeder.log', 'a') as f:
					f.write(f'\n{result.stderr.decode()}')
				# only add new database entry if download completed successfully
				if result.returncode == 0:
					# make the file path prettier and change metadata
					track = result.stdout.rstrip().decode()
					file_path, title = update_track_data(track, artist)
					new_track = Tracks(title=title, artist=artist, config='pf', station='new', file_path=file_path)
					db.session.add(new_track)
					db.session.commit()
					print(f'Added {file_path}')
				if downloads == num_links:
					with open('dl_data/pf_download_status', 'w') as f:
						f.write('Done')
				else:
					downloads += 1


@celery_app.task
def upload(file_path):
	populateDb(file_path)
	requests.get('http://gateway/upload_complete')
