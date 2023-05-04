from flask import render_template, request, redirect
from webapp import *
from stringwave import *
import subprocess
import re
import os
from pathlib import Path


@app.route('/tracks')
def radio():
	return render_template('index.html', tracks=Tracks.query.order_by(Tracks.track_id).all())


@app.route('/download', methods = ['POST'])
def download():
	data = request.get_json()
	app = data['app']
	if app == 'cogmera':
		filename = data['filename']
		search_query = data['search_query']
		config = data['config']
		output = subprocess.run([f'{os.getcwd()}/scripts/cogmera-download.sh', filename, search_query, config], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		with open(cogmera_log, 'a') as f:
			f.write(output.stdout.decode())
		#failed_downloads += int(str(output.stdout).count('Downloading 0 items of 0'))
		#print(f'Number of failed downloads: {failed_downloads}\n')
		#if failed_downloads > 0:
		#	downloadSongs(albums, num_albums_to_pick - failed_downloads, config_stamp)
		output = subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'new'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		with open(cogmera_log, 'a') as f:
			f.write(output.stdout.decode())
		new_track = Tracks(filename=filename, config=config)
		db.session.add(new_track)
		db.session.commit()
		return 'Complete!'
	elif app == 'pipefeeder':
		links = data['links']
		open(pipefeeder_log, 'w').close()
		for link in links:
			regex = r'^(https?:\/\/)?(www\.)?youtube\.com/watch\?v=.{11}$'
			if not re.match(regex, link):
				return 'Invalid YouTube link.'
			output = subprocess.run([f'{os.getcwd()}/scripts/pipefeeder-download.sh', link], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			with open(pipefeeder_log, 'a') as f:
				f.write(output.stdout.decode())
			output = subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'new'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			with open(cogmera_log, 'a') as f:
				f.write(output.stdout.decode())
			tracks = os.listdir('/stringwave/radio/new')
			latest_track = Path(max(tracks, key=os.path.getctime)).stem
			new_track = Tracks(filename=latest_track, config="pf")
			db.session.add(new_track)
			db.session.commit()
			return 'Complete!'
	else:
		return 'Not a valid application'
	output = subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'new'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	if app == 'cogmera':
		with open(cogmera_log, 'a') as f:
			f.write(output.stdout.decode())
	if app == 'pipefeeder':
		with open(pipefeeder_log, 'a') as f:
			f.write(output.stdout.decode())
	


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False)
