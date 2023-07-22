from flask import render_template, request, redirect, flash, jsonify
from werkzeug.utils import secure_filename
from sqlalchemy import func, exc
from webapp import app, db, allowed_file, Config, Tracks, Subs, Genres, Styles, Countries, Decades, Years, SortMethods
import subprocess
import os
from tasks import move_track, download_track, upload
from pipefeeder import getChannelFeed, getChannelId, getChannelName, getChannelUrl, getChannelIcon
import sqlite3
import re


@app.route('/', methods = ['GET'])
def index():
	return render_template('index.html')


@app.route('/tracks/<string:station>', methods = ['GET'])
def tracks_main(station):
	return render_template('tracks.html', tracks=Tracks.query.filter(Tracks.station == station).order_by(Tracks.track_id).all(), station=station)


@app.route('/radio/<string:station>', methods = ['GET'])
def radio_main(station):
	return render_template('radio.html', station=station)


@app.route('/move_to_main', methods = ['POST'])
def move_to_main():
	track = db.session.query(Tracks).filter_by(track_id=request.form['move_to_main']).one()
	track = track.title.replace(' ', '_')
	entry = db.session.query(Tracks).filter_by(track_id=request.form['move_to_main']).one()
	entry.station = 'main'
	db.session.commit()
	move_track.delay(track)
	return render_template('move.html')


@app.route('/move_complete', methods = ['GET'])
def move_complete():
	with open('webapp/static/move_status', 'w') as f:
		f.write('complete')
		print('complete')


@app.route('/move_status', methods = ['GET'])
def move_status():
	with open('webapp/static/move_status', 'r') as f:
		status = f.read()
	json = f'{{ "status": "{status}" }}'
	return json


@app.route('/delete_track/<string:station>', methods = ['POST'])
def delete_track(station):
	track = db.session.query(Tracks).filter_by(track_id=request.form['delete_track']).one()
	os.remove(f'/stringwave/radio/{station}/{track.title.replace(" ", "_")}.opus')
	db.session.query(Tracks).filter_by(track_id=request.form['delete_track']).delete()
	db.session.commit()
	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', station])
	return redirect(f'/tracks/{station}')


@app.route('/skip/<string:station>', methods = ['GET'])
def skip(station):
	if station != 'new' and station != 'main':
		flash('Invalid Station')
		return redirect(f'/radio_{station}')
	else:
		subprocess.run(['./scripts/ezstream-skip.sh', station])
		return jsonify({'station_skipped': station})


@app.route('/download/<string:app>', methods = ['GET'])
def download(app):
	download_track.delay(app)
	return 'Complete!'


@app.route('/reread/<string:station>', methods = ['GET'])
def reread(station):
	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', station])
	return 'Playlist reread.'


@app.route('/cogmera/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        genres = request.form.getlist('genres')
        genres = ';'.join(genres)
        styles = request.form.getlist('styles')
        styles = ';'.join(styles)
        decade = request.form['decades']
        year = request.form['years']
        country = request.form['countries']
        sort_method = request.form['sort_methods']
        sort_order = request.form['order']
        albums_to_find = request.form['number']
        new_config = Config(
						genres=genres, 
						styles=styles, 
						decade=decade, 
						year=year, 
						country=country, 
						sort_method=sort_method, 
						sort_order=sort_order, 
						albums_to_find=albums_to_find)
        db.session.add(new_config)
        db.session.commit()
    return render_template(
							'config.html', 
							genres=Genres.query.order_by(Genres.genre_id).all(), 
							styles=Styles.query.order_by(Styles.style_id).all(), 
							decades=Decades.query.order_by(Decades.decade_id).all(), 
							countries=Countries.query.order_by(Countries.country_id).all(), 
							years=Years.query.order_by(Years.year_id).all(), 
							sort_methods=SortMethods.query.order_by(SortMethods.sort_method_id).all())


@app.route('/cogmera/dump_config', methods=['GET'])
def dump():
	configs = Config.query.order_by(Config.config_id).all()
	return render_template('dump_config.html', configs=configs) 


@app.route('/cogmera/delete_config', methods=['POST'])
def delete():
	db.session.query(Config).filter_by(config_id=request.form['delete_config']).delete()
	db.session.commit()
	return redirect('/cogmera/dump_config')	


@app.route('/cogmera/backup_configs', methods = ['GET'])
def backup_configs():
	con = sqlite3.connect('webapp/instance/stringwave.db')
	configs = con.cursor().execute('SELECT * FROM config')
	with open('webapp/static/configs.txt', 'w') as f:
		#[f.write(f'{"|".join(config[1:])}\n') for config in configs.fetchall()]
		for config in configs.fetchall():
			config = [str(item) for item in config[1:]]
			config = '|'.join(config)
			f.write(config + '\n')
	return '<a href="/static/configs.txt" download>Download</a><br><a href="/cogmera/dump_config">Return to Configs</a>'


@app.route('/pipefeeder/list_subs', methods = ['GET'])
def listSubs():
	return render_template('subs.html', subs=Subs.query.order_by(func.lower(Subs.channel_name)).all())


@app.route('/pipefeeder/add_sub', methods = ['POST'])
def addSub():
	channel_url = request.form['subscribe']
	regex = r'^(((https?):\/\/)?(www\.)?youtube\.com)/(c(hannel)?/|@).+$'
	if not re.match(regex, channel_url):
		print(f'{channel_url} is not valid')
		flash('Not a valid YouTube URL')
		return redirect('/pipefeeder/list_subs')
	feed = getChannelFeed(channel_url)
	new_record = Subs(
					channel_id=getChannelId(feed), 
					channel_name=getChannelName(feed), 
					channel_url=getChannelUrl(feed), 
					channel_icon=getChannelIcon(channel_url))
	try:
		db.session.add(new_record)
	except exc.IntegrityError:
		print('Duplicate subscription')
		flash('Duplicate subscription')
		return redirect('/pipefeeder/list_subs')
	db.session.commit()
	return redirect('/pipefeeder/list_subs')


@app.route('/pipefeeder/del_sub', methods = ['POST'])
def delSub():
	db.session.query(Subs).filter_by(channel_id=request.form['unsubscribe']).delete()
	db.session.commit()
	return redirect('/pipefeeder/list_subs')


@app.route('/pipefeeder/backup_subs', methods = ['GET'])
def backup():
	con = sqlite3.connect('webapp/instance/stringwave.db')
	urls = con.cursor().execute('SELECT channel_url FROM subs')
	with open('webapp/static/subs.txt', 'w') as f:
		[f.write(f'{url[0]}\n') for url in urls.fetchall()]
	return '<a href="/static/subs.txt" download>Download</a><br><a href="/pipefeeder/list_subs">Return to Subs</a>'


@app.route('/pipefeeder/upload_subs', methods = ['GET', 'POST'])
def upload_subs():
	with open('webapp/static/upload_status', 'w') as f:
		f.write('uploading')
	file = request.files['subs']
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		file.save(file_path)
	upload.delay(file_path)
	return render_template('upload.html')


@app.route('/pipefeeder/upload_complete', methods = ['GET'])
def upload_complete():
	with open('webapp/static/upload_status', 'w') as f:
		f.write('complete')
		return('complete')


@app.route('/pipefeeder/upload_status', methods = ['GET'])
def upload_status():
	with open('webapp/static/upload_status', 'r') as f:
		status = f.read()
	json = f'{{ "status": "{status}"}}'
	return json


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
