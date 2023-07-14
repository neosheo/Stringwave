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
#	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'new'])
#	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'main'])
	requests.get('http://gateway/reread/new')
	requests.get('http://gateway/reread/main')
	requests.get('http://gateway/move_complete')


@celery_app.task
def download_track(app):
	match app:
		case 'cogmera':
			with open('dl_data/search_queries', 'r') as f:
				data = json.load(f)
			filename = re.sub(r'(\||%|&|:|;|,|-|\*|#|\\|/|\[|\])', '', data['filename'])
			artist = data['artist']
			search_query = data['search_query']
			config = data['config']
			# with open('dl_data/downloads_attempted', 'r+') as f:
			# 	# prevent exit if read returns empty string
			# 	while True:
			# 		try:
			# 			downloads_attempted = int(f.read().strip())
			# 		except ValueError:
			# 			continue
			# 		break				
			# 	f.seek(0)
			# 	f.truncate()
			# 	f.write(str(downloads_attempted + 1))
			output = subprocess.run([f'{os.getcwd()}/scripts/cogmera-download.sh', filename, artist, search_query, config])#, capture_output=True)
			# with open(cogmera_log, 'a') as f:
			# 	f.write(output.stdout.decode())
			new_track = Tracks(title=filename, artist=artist, config=config, station='new')
			db.session.add(new_track)
			db.session.commit()
			# with open('dl_data/completed_downloads_cogmera', 'r+') as f:
			# 	while True:
			# 		try:
			# 			num_completed_downloads = int(f.read(2).strip()) + 1
			# 		except ValueError:
			# 			continue
			# 		break
			# 	print(num_completed_downloads)
			# 	f.seek(0)
			# 	f.truncate()
			# 	f.write(str(num_completed_downloads))
		case 'pipefeeder':
			with open('dl_data/urls', 'r') as f:
				links = f.readlines()
			if links == []: 
				print('No videos to download')
				return 'No links to download.'
			# do this before downloading so you can compare the amount of files in the directory later
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
					print(f'Invalid YouTube link at line {line}.')
					return
				print(f'Downloading {link}')
				output = subprocess.run([f'{os.getcwd()}/scripts/pipefeeder-download.sh', link])#, capture_output=True)
				# with open(pipefeeder_log, 'a') as f:
				# 	f.write(output.stdout.decode())
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
				# with open('.completed_downloads', 'r+') as f:
				# 	num_completed_downloads = int(len(f.read())) + 1
				# 	f.write(num_completed_downloads)


@celery_app.task
def upload(file_path):
	populateDb(file_path)
	requests.get('http://gateway/upload_complete')
