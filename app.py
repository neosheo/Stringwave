from flask import render_template, request, redirect, flash
from werkzeug.utils import secure_filename
from sqlalchemy import func
from webapp import *
import subprocess
import os
from tasks import move_track, download_track, upload
import time
from cogmera import *
from pipefeeder import *
import sqlite3
import re


@app.route('/tracks/<station>', methods = ['GET'])
def tracks_main(station):
	return render_template('index.html', tracks=Tracks.query.filter(Tracks.station == station).order_by(Tracks.track_id).all())


@app.route('/radio/<station>', methods = ['GET'])
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
	return render_template('/move.html')


@app.route('/move_complete', methods = ['GET'])
def move_complete():
	with open('webapp/static/move_status', 'w') as f:
		f.write('complete')


@app.route('/move_status', methods = ['GET'])
def move_status():
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


@app.route('/download/<app>', methods = ['GET'])
def download(app):
	download_track.delay(app)
		# with open('urls/urls', 'r') as f:
		# 	links = f.readlines()
		# if links == []: 
		# 	print('No videos to download')
		# 	return 'No links to download.'
		# for line, link in enumerate(links):
		# 	link = link.strip()
		# 	download_pf_track.delay(line, link)
		# 	return 'Download queued.'
	# if request.method == 'POST':
	# 	data = request.get_json()
	# 	download_cm_track.delay(data)
	# 	return 'Download queued.'
	return 'Complete!'


# @app.route('/check_download_completion/<app>', methods = ['GET'])
# def check_downloads_completion(app):
# 	match app:
# 		case 'cogmera':
# 			with open('dl_data/downloads_attempted', 'r') as f:
# 				number_of_downloads = f.read().strip()
# 				# to prevent program from erroring if cogmera is editing file at same time as reading
# 				if number_of_downloads == '': return
# 		case 'pipefeeder':
# 			with open('dl_data/urls', 'r') as f:
# 				number_of_downloads = len(f.readlines())
# 	print(f'Number of downloads: {number_of_downloads}')
# 	with open(f'dl_data/completed_downloads_{app}', 'w') as f:
# 		f.write('0')
# 	while True:
# 		with open(f'dl_data/completed_downloads_{app}', 'r') as f:
# 			completed_downloads = f.read()
# 			if int(completed_downloads) == number_of_downloads:
# 				print('Downloads complete!')
# 				break
# 			time.sleep(5)
# 	return redirect('/reread')


@app.route('/reread', methods = ['GET'])
def reread():
	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'new'])
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
        new_config = Config(genres=genres, styles=styles, decade=decade, year=year, country=country, sort_method=sort_method, sort_order=sort_order, albums_to_find=albums_to_find)
        db.session.add(new_config)
        db.session.commit()
    return render_template('config.html', genres=Genres.query.order_by(Genres.genre_id).all(), styles=Styles.query.order_by(Styles.style_id).all(), decades=Decades.query.order_by(Decades.decade_id).all(), countries=Countries.query.order_by(Countries.country_id).all(), years=Years.query.order_by(Years.year_id).all(), sort_methods=SortMethods.query.order_by(SortMethods.sort_method_id).all())


@app.route('/cogmera/dump_config', methods=['GET'])
def dump():
	configs = Config.query.order_by(Config.config_id).all()
	return render_template('dump_config.html', configs=configs) 


@app.route('/cogmera/delete_config', methods=['POST'])
def delete():
	db.session.query(Config).filter_by(config_id=request.form['delete_config']).delete()
	db.session.commit()
	return redirect('/cogmera/dump_config')	


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
	new_record = Subs(channel_id=getChannelId(feed), channel_name=getChannelName(feed), channel_url=getChannelUrl(feed), channel_icon=getChannelIcon(channel_url))
	try:
		db.session.add(new_record)
	except sqlalchemy.exc.IntegrityError:
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
	con = sqlite3.connect('webapp/instance/subs.db')
	urls = con.cursor().execute('SELECT channel_url FROM subs')
	with open('backup/subs.txt', 'w') as f:
		[f.write(f'{url[0]}\n') for url in urls.fetchall()]
	return '<a href="/pipefeeder/list_subs">Done!</a>'


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


@app.route('/pipefeeder/upload_status', methods = ['GET'])
def upload_status():
	with open('webapp/static/upload_status', 'r') as f:
		status = f.read()
	json = f'{{ "status": "{status}"}}'
	return json


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
