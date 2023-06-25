from webapp import celery_app, db, Tracks, cogmera_log, pipefeeder_log
import requests
import os
import subprocess
import re
from pathlib import Path
import shutil


@celery_app.task
def move_track(track):
	if track[-5:] != '.opus':
		track = f'{track}.opus'
	subprocess.run(['mv', f'/stringwave/radio/new/{track}', f'/stringwave/radio/main/{track}'])
	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'new'])
	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'main'])
	requests.get('http://gateway/move_complete')


@celery_app.task
def download_cm_track(data):
	filename = re.sub(r'(\||%|&|:|;|,|-|\*|#|\\|/|\[|\])', '', data['filename'])
	artist = data['artist']
	search_query = data['search_query']
	config = data['config']
	output = subprocess.run([f'{os.getcwd()}/scripts/cogmera-download.sh', filename, artist, search_query, config], capture_output=True)
	with open(cogmera_log, 'a') as f:
		f.write(output.stdout.decode())
	new_track = Tracks(title=f'{filename}.opus', artist=artist, config=config, station='new')
	db.session.add(new_track)
	db.session.commit()
	with open('.completed_downloads', 'r+') as f:
		num_completed_downloads = int(f.read()) + 1
		f.write(str(num_completed_downloads))


@celery_app.task
def download_pf_track(line, link):
	# do this before downloading so you can compare the amount of files in the directory later
	print('Cleaning broken downloads...')
	for file in os.listdir('/stringwave/radio/new'):
	# delete directories with files in them which are created by failed downloads
		if os.path.isdir(f'/stringwave/radio/new/{file}'):
			shutil.rmdir(f'/stringwave/radio/new/{file}')
	print('Done!')
	regex = r'^(https?:\/\/)?(www\.)?youtube\.com\/(watch\?)?v(=|\/).{11}$'
	if not re.match(regex, link):
		print(f'Invalid YouTube link at line {line}.')
		return
	print(f'Downloading {link}')
	# number of files in the directory before and after download will be compared to prevent adding unecessary files to database
	tracks = os.listdir('/stringwave/radio/new')
	for track in tracks:
		if track == '.playlist':
			del track
			continue
		print(track)
	num_tracks_before = len(os.listdir('/stringwave/radio/new'))
	print(f'Number of tracks before download: {num_tracks_before}')
	output = subprocess.run([f'{os.getcwd()}/scripts/pipefeeder-download.sh', link], capture_output=True)
	with open(pipefeeder_log, 'a') as f:
		f.write(output.stdout.decode())
	tracks = os.listdir('/stringwave/radio/new')
	num_tracks_after = len(tracks)
	print(f'Number of tracks after download: {num_tracks_after}')
	for track in tracks:
		if track == '.playlist':
			del track
			continue
		print(track)
		# remove .playlist from list incase it somehow is most recently created file
	tracks_with_path = [ f'/stringwave/radio/new/{track}' for track in tracks ]
	# grab most recently downloaded track and add its info to database
	latest_track = Path(max(tracks_with_path, key=os.path.getctime)).stem
	print(f'Latest track: {latest_track}')
	new_track = Tracks(title=latest_track, config='pf', station='new')
	db.session.add(new_track)
	db.session.commit()
	with open('.completed_downloads', 'r+') as f:
		num_completed_downloads = int(f.read()) + 1
		f.write(num_completed_downloads)
