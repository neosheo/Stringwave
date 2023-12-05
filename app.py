from flask import render_template, request, redirect, flash, jsonify, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy import func, exc
from webapp import (
	app, 
	db,
	flask_bcrypt, 
	Users, 
	LoginForm,
	login_manager,
	allowed_file, 
	Config, 
	Tracks, 
	Subs, 
	Genres, 
	Styles, 
	Countries, 
	Decades, 
	Years, 
	SortMethods)
import subprocess
import os
from tasks import move_track, download_track, upload
from pipefeeder import (
	get_channel_feed, 
	get_channel_id, 
	get_channel_name, 
	get_channel_url, 
	get_channel_icon)
import sqlite3
import re
from mutagen.oggopus import OggOpus


@app.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			user = db.session.query(Users).filter(Users.username == form.username.data).one()
			if user and flask_bcrypt.check_password_hash(user.password, form.password.data):
				login_user(user, remember=True)
				next = request.args.get('next')
				return redirect(next or '/')
			else:
				flash("Login unsuccessful.")
				return render_template("login.html", form=form)
	else:
		return render_template('login.html', form=form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect('/login')


@login_manager.user_loader
def load_user(username):
	user = db.session.query(Users).filter(Users.username == username).one()
	if not user:
		return None
	return user


@app.route('/', methods = ['GET'])
def index():
	return render_template('index.html')


@app.route('/tracks/<string:station>', methods = ['GET'])
@login_required
def tracks_main(station):
	tracks = db.session.query(Tracks).filter(Tracks.station == station).order_by(func.lower(Tracks.title)).all()
	for track in tracks:
		track.title = re.sub(r'_+', ' ', track.title)
		track.title = re.sub(r'\s{2,}', ' ', track.title)
	db.session.commit()
	return render_template('tracks.html', tracks=tracks, station=station)


@app.route('/radio/<string:station>', methods = ['GET'])
def radio_main(station):
	return render_template('radio.html', station=station)


@app.route('/update_title', methods = ['POST'])
@login_required
def update_title():
	data = request.form['update-title'].split(';')
	track_id = data[0]
	new_name = data[1].strip()
	station = data[2]
	track = db.session.query(Tracks).filter_by(track_id=track_id).one()
	track.title = new_name
	db.session.commit()
	file_path = db.session.query(Tracks).filter_by(track_id=track_id).one().file_path
	file = OggOpus(file_path)
	file['title'] = new_name
	file.save()
	return redirect(f'/tracks/{station}')


@app.route('/update_artist', methods = ['POST'])
@login_required
def update_artist():
	data = request.form['update-artist'].split(';')
	track_id = data[0]
	new_name = data[1].strip()
	station = data[2]
	track = db.session.query(Tracks).filter_by(track_id=track_id).one()
	track.artist = new_name
	db.session.commit()
	file_path = db.session.query(Tracks).filter_by(track_id=track_id).one().file_path
	file = db.session.query(Tracks).filter_by(track_id=track_id).one().title.replace(' ', '_')
	file = OggOpus(file_path)
	file['artist'] = new_name
	file.save()
	return redirect(f'/tracks/{station}')


@app.route('/move_to_main', methods = ['POST'])
@login_required
def move_to_main():
	track_id = request.form['move_to_main']
	old_file_path = db.session.query(Tracks).filter_by(track_id=track_id).one().file_path
	new_file_path = old_file_path.replace('/new/', '/main/')
	move_track.delay(track_id, old_file_path, new_file_path)
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
@login_required
def delete_track(station):
	file_path = db.session.query(Tracks).filter_by(track_id=request.form['delete_track']).one().file_path
	os.remove(file_path)
	db.session.query(Tracks).filter_by(track_id=request.form['delete_track']).delete()
	db.session.commit()
	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', station])
	return redirect(f'/tracks/{station}')


@app.route('/skip/<string:station>', methods = ['GET'])
@login_required
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
@login_required
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
@login_required
def dump():
	configs = Config.query.order_by(Config.config_id).all()
	return render_template('dump_config.html', configs=configs) 


@app.route('/cogmera/delete_config', methods=['POST'])
@login_required
def delete():
	db.session.query(Config).filter_by(config_id=request.form['delete_config']).delete()
	db.session.commit()
	return redirect('/cogmera/dump_config')	


@app.route('/cogmera/backup_configs', methods = ['GET'])
@login_required
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
@login_required
def listSubs():
	return render_template('subs.html', subs=Subs.query.order_by(func.lower(Subs.channel_name)).all())


@app.route('/pipefeeder/add_sub', methods = ['POST'])
@login_required
def addSub():
	channel_url = request.form['subscribe']
	regex = r'^(((https?):\/\/)?(www\.)?youtube\.com)/(c(hannel)?/|@).+$'
	if not re.match(regex, channel_url):
		print(f'{channel_url} is not valid')
		flash('Not a valid YouTube URL')
		return redirect('/pipefeeder/list_subs')
	feed = get_channel_feed(channel_url)
	new_record = Subs(
					channel_id=get_channel_id(feed), 
					channel_name=get_channel_name(feed), 
					channel_url=get_channel_url(feed), 
					channel_icon=get_channel_icon(channel_url))
	try:
		db.session.add(new_record)
	except exc.IntegrityError:
		print('Duplicate subscription')
		flash('Duplicate subscription')
		return redirect('/pipefeeder/list_subs')
	db.session.commit()
	return redirect('/pipefeeder/list_subs')


@app.route('/pipefeeder/del_sub', methods = ['POST'])
@login_required
def delSub():
	db.session.query(Subs).filter_by(channel_id=request.form['unsubscribe']).delete()
	db.session.commit()
	return redirect('/pipefeeder/list_subs')


@app.route('/pipefeeder/backup_subs', methods = ['GET'])
@login_required
def backup():
	con = sqlite3.connect('webapp/instance/stringwave.db')
	urls = con.cursor().execute('SELECT channel_url FROM subs')
	with open('webapp/static/subs.txt', 'w') as f:
		[f.write(f'{url[0]}\n') for url in urls.fetchall()]
	return '<a href="/static/subs.txt" download>Download</a><br><a href="/pipefeeder/list_subs">Return to Subs</a>'


@app.route('/pipefeeder/upload_subs', methods = ['GET', 'POST'])
@login_required
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
