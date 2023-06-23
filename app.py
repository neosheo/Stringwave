from flask import render_template, request, redirect, flash
from webapp import *
import subprocess
import re
import os
from pathlib import Path
import shutil
from move_track import move_track


cogmera_log = '/stringwave/logs/cogmera_download.log'
pipefeeder_log = '/stringwave/logs/pipefeeder.log'


@app.route('/tracks_main')
def tracks_main():
	return render_template('index.html', tracks=Tracks.query.filter(Tracks.station == 'main').order_by(Tracks.track_id).all())


@app.route('/radio_main')
def radio_main():
	return render_template('radio.html', station='main')


@app.route('/tracks_new')
def tracks_new():
	return render_template('index.html', tracks=Tracks.query.filter(Tracks.station == 'new').order_by(Tracks.track_id).all())


@app.route('/radio_new')
def radio_new():
	return render_template('radio.html', station='new')


@app.route('/move_to_main', methods = ['POST'])
def move_to_main():
	track = db.session.query(Tracks).filter_by(track_id=request.form['move_to_main']).one()
	track = track.title.replace(' ', '_')
	entry = db.session.query(Tracks).filter_by(track_id=request.form['move_to_main']).one()
	print(entry)
	entry.station = 'main'
	db.session.commit()
	move_track.delay(track)
	return render_template('/move.html')


@app.route('/move_complete', methods = ['GET'])
def upload_complete():
	with open('webapp/static/move_status', 'w') as f:
		f.write('complete')


@app.route('/move_status', methods = ['GET'])
def upload_status():
	with open('webapp/static/move_status', 'r') as f:
		status = f.read()
	json = f'{{ "status": "{status}"}}'
	return json


@app.route('/delete_track', methods = ['POST'])
def delete_track():
	track = db.session.query(Tracks).filter_by(track_id=request.form['delete_track']).one()
	os.remove(f'/stringwave/radio/new/{track.title}')
	db.session.query(Tracks).filter_by(track_id=request.form['delete_track']).delete()
	db.session.commit()
	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'new'])
	return redirect('/tracks_new')


@app.route('/skip/<station>', methods = ['GET'])
def skip(station):
	if station != 'new' and station != 'main':
		flash('Invalid Station')
		return redirect(f'/radio_{station}')
	else:
		subprocess.run(['./scripts/ezstream-skip.sh', station])
		return redirect(f'/radio_{station}')


@app.route('/download', methods = ['POST'])
def download():
	data = request.get_json()
	app = data['app']
	if app == 'cogmera':
		filename = re.sub(r'(\||%|&|:|;|,|-|\*|#|\\|/)', data['filename'])
		#filename = data['filename'].replace('|', '_').replace('%', '_').replace('&', '_').replace(':', '_').replace(';', '_').replace(',', '_').replace('-', '_').replace('*', '_').replace('#', '_').replace('/', '_').replace('\\', '_')
		artist = data['artist']
		search_query = data['search_query']
		config = data['config']
		output = subprocess.run([f'{os.getcwd()}/scripts/cogmera-download.sh', filename, artist, search_query, config], capture_output=True)
		with open(cogmera_log, 'a') as f:
			f.write(output.stdout.decode())
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
			print(f'Downloading {link}')
			output = subprocess.run([f'{os.getcwd()}/scripts/pipefeeder-download.sh', link], capture_output=True)
			with open(pipefeeder_log, 'a') as f:
				f.write(output.stdout.decode())
			for file in os.listdir('/stringwave/radio/new'):
			# delete directories with files in them which are created by failed downloads
				if os.path.isdir(f'/stringwave/radio/new/{file}'):
					shutil.rmdir(f'/stringwave/radio/new/{file}')
			tracks = os.listdir('/stringwave/radio/new')
			tracks_with_path = [ f'/stringwave/radio/new/{track}' for track in tracks ]
			latest_track = Path(max(tracks_with_path, key=os.path.getctime)).stem
			new_track = Tracks(title=latest_track, config='pf', station='new')
			db.session.add(new_track)
			db.session.commit()
	else:
		return 'Not a valid application'
	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'new'])
	return "Complete!"


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
