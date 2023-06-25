from flask import render_template, request, redirect, flash
from webapp import app, db, Tracks, cogmera_log, pipefeeder_log
import subprocess
import os
from tasks import move_track, download_cm_track, download_pf_track
import time


@app.route('/tracks/<station>')
def tracks_main(station):
	return render_template('index.html', tracks=Tracks.query.filter(Tracks.station == station).order_by(Tracks.track_id).all())


@app.route('/radio/<station>')
def radio_main(station):
	return render_template('radio.html', station=station)


# @app.route('/tracks_new')
# def tracks_new():
# 	return render_template('index.html', tracks=Tracks.query.filter(Tracks.station == 'new').order_by(Tracks.track_id).all())


# @app.route('/radio_new')
# def radio_new():
# 	return render_template('radio.html', station='new')


@app.route('/move_to_main', methods = ['POST'])
def move_to_main():
	track = db.session.query(Tracks).filter_by(track_id=request.form['move_to_main']).one()
	track = track.title.replace(' ', '_')
	entry = db.session.query(Tracks).filter_by(track_id=request.form['move_to_main']).one()
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
	json = f'{{ "status": "{status}" }}'
	return json


@app.route('/delete_track', methods = ['POST'])
def delete_track():
	track = db.session.query(Tracks).filter_by(track_id=request.form['delete_track']).one()
	os.remove(f'/stringwave/radio/new/{track.title.replace(" ", "_")}')
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


# pipefeeder sends a GET request, cogmera sends a POST request
@app.route('/download', methods = ['GET', 'POST'])
def download():
	if request.method == 'GET':
		with open('urls/urls', 'r') as f:
			links = f.readlines()
		if links == []: 
			print('No videos to download')
			return 'No links to download.'
		for line, link in enumerate(links):
			link = link.strip()
			download_pf_track.delay(line, link)
			return 'Download queued.'
	if request.method == 'POST':
		data = request.get_json()
		download_cm_track.delay(data)
		return 'Download queued.'
	return 'Invalid request.'


@app.route('/check_download_completion/<app>', methods = ['GET'])
def check_downloads_completion(app):
	match app:
		case 'cogmera':
			number_of_downloads = os.getenv('NUM_DAILY_DOWNLOADS')
		case 'pipefeeder':
			with open('urls/urls', 'r') as f:
				number_of_downloads = len(f.readlines())
	while True:
		with open(f'.completed_downloads_{app}', 'r') as f:
			completed_downloads = f.read()
			if completed_downloads == number_of_downloads:
				break
			time.sleep(5)
	return redirect('/reread')


@app.route('/reread', methods = ['GET'])
def reread():
	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'new'])
	return 'Playlist reread.'


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
