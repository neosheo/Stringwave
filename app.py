from flask import render_template, request, redirect
from webapp import *
import subprocess
import re
import os
from pathlib import Path
import shutil


cogmera_log = '/stringwave/logs/cogmera_download.log'
pipefeeder_log = '/stringwave/logs/pipefeeder.log'


@app.route('/tracks_main')
def tracks_main():
	return render_template('index.html', tracks=Tracks.query.filter(Tracks.station == 'main').order_by(Tracks.track_id).all())


@app.route('/tracks_new')
def tracks_new():
	return render_template('index.html', tracks=Tracks.query.filter(Tracks.station == 'new').order_by(Tracks.track_id).all())


@app.route('/move_to_main', methods = ['POST'])
def move_to_main():
	track = db.session.query(Tracks).filter_by(track_id=request.form['move_to_main']).one()
	track = track.title.replace(' ', '_')
	db.session.query(Tracks).filter_by(track_id=request.form['move_to_main']).station = 'main'
	db.session.commit()
	os.rename(f'/stringwave/radio/new/{track}', f'/stringwave/radio/main/{track}')
	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'new'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'main'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	return redirect('/tracks_main')



@app.route('/delete_track', methods = ['POST'])
def delete_track():
	track = db.session.query(Tracks).filter_by(track_id=request.form['delete_track']).one()
	os.remove(f'/stringwave/radio/new/{track.title}')
	db.session.query(Tracks).filter_by(track_id=request.form['delete_track']).delete()
	db.session.commit()
	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'new'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	return redirect('/tracks_new')


@app.route('/download', methods = ['POST'])
def download():
	data = request.get_json()
	app = data['app']
	if app == 'cogmera':
		filename = data['filename']
		artist = data['artist']
		search_query = data['search_query']
		config = data['config']
		output = subprocess.run([f'{os.getcwd()}/scripts/cogmera-download.sh', filename, artist, search_query, config], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		with open(cogmera_log, 'a') as f:
			f.write(output.stdout.decode())
		#failed_downloads += int(str(output.stdout).count('Downloading 0 items of 0'))
		#print(f'Number of failed downloads: {failed_downloads}\n')
		#if failed_downloads > 0:
		#	downloadSongs(albums, num_albums_to_pick - failed_downloads, config_stamp)
		# output = subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'new'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		# with open(cogmera_log, 'a') as f:
		# 	f.write(output.stdout.decode())
		new_track = Tracks(title=f'{filename}.opus', artist=artist, config=config, station='new')
		db.session.add(new_track)
		db.session.commit()
	elif app == 'pipefeeder':
		links = data['links']
		for link in links:
			regex = r'^(https?:\/\/)?(www\.)?youtube\.com\/(watch\?)?v(=|\/).{11}$'
			if not re.match(regex, link):
				print('Invalid YouTube link.')
				return '<h1>Invalid YouTube link.</h1>'
			output = subprocess.run([f'{os.getcwd()}/scripts/pipefeeder-download.sh', link], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			with open(pipefeeder_log, 'a') as f:
				f.write(output.stdout.decode())
			for file in os.listdir('/stringwave/radio/new'):
				if os.path.isdir(f'/stringwave/radio/new/{file}'):
					shutil.rmdir(f'/stringwave/radio/new/{file}')
			tracks = os.listdir('/stringwave/radio/new')
			latest_track = Path(max(tracks, key=os.path.getctime)).stem
			new_track = Tracks(title=latest_track, config='pf', station='new')
			db.session.add(new_track)
			db.session.commit()
	else:
		return 'Not a valid application'
	output = subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'new'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#	if app == 'cogmera':
#		with open(cogmera_log, 'a') as f:
#			f.write(output.stdout.decode())
#	if app == 'pipefeeder':
#		with open(pipefeeder_log, 'a') as f:
#			f.write(output.stdout.decode())
	return "Complete!"
	


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False)
