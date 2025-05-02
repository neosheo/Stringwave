from flask import (
	render_template,
	request,
	redirect,
	flash,
	jsonify)
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
	SortMethods,
	sw_logger as logger)
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
			# select user matching supplied user name
			user = db.session.query(Users).filter(Users.username == form.username.data).one()

			# check if password hash matches user's password hash
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
	# filter only tracks from the supplied station for display
	tracks = db.session.query(Tracks).filter(Tracks.station == station).order_by(func.lower(Tracks.title)).all()
	for track in tracks:
		# replace underscores and multiple consecutive spaces with a single space
		track.title = re.sub(r'_+', ' ', track.title)
		track.title = re.sub(r'\s{2,}', ' ', track.title)
	return render_template('tracks.html', tracks=tracks, station=station)


@app.route('/radio/<string:station>', methods = ['GET'])
def radio_main(station):
	return render_template('radio.html', station=station)


@app.route('/update_track_data', methods = ['POST'])
@login_required
def update_track_data():
	data = request.form['update-track-data'].split(';')
	# parse track metadata from POST request
	track_id = data[0]
	new_title = data[1].strip()
	new_artist = data[2].strip()
	station = data[3]

	# find requested track in database based on track_id
	track = db.session.query(Tracks).filter_by(track_id=track_id).one()

	# set metadata in database
	track.title = new_title
	track.artist = new_artist
	db.session.commit()

	# extract file path from database and set new metadata to file
	file_path = db.session.query(Tracks).filter_by(track_id=track_id).one().file_path
	file = OggOpus(file_path)
	file['title'] = new_title
	file['artist'] = new_artist
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


# sets regex pattern to extract title and artist from pipefeeder video title
@app.route('/add_regex', methods = ['POST'])
@login_required
def add_regex():
	data = request.get_json()

	# extract subscription info from POST request
	channel_id = data["channel_id"]
	video_title_regex = data["video_title_regex"]
	regex_type = data["regex_type"]

	# add regex pattern to database
	channel = db.session.query(Subs).filter_by(channel_id=channel_id).scalar()
	channel.video_title_regex = video_title_regex
	channel.regex_type = regex_type
	db.session.commit()
	return "Success"


# move a track from the new station to the main station
@app.route('/move_to_main', methods = ['POST'])
@login_required
def move_to_main():
	track_id = request.form['move_to_main']
	old_file_path = db.session.query(Tracks).filter_by(track_id=track_id).one().file_path
	new_file_path = old_file_path.replace('/new/', '/main/')
	move_track.delay(track_id, old_file_path, new_file_path)
	return render_template('move.html')


# this is called by the celery backend when the move is complete
# this causes the tracks page to reload
@app.route('/move_complete', methods = ['GET'])
def move_complete():
	with open('webapp/static/move_status', 'w') as f:
		f.write('complete')
		return('complete')


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


# play now will either be 1 (true) or 0 (false)
@app.route('/queue/<string:play_now>/<string:station>', methods = ['POST'])
@login_required
def queue_track(play_now: str, station: str):
	if station != 'new' and station != 'main':
		flash('Invalid Station')
		return redirect(f'/tracks/{station}')
	else:
		# extract list of queued track ids
		queued_tracks = request.get_json()

		# create an empty list to fill with track names
		queued_track_names = []

		# convert track ids to track names
		for track_id in queued_tracks:
			# extract file path
			file_path = db.session.query(Tracks).filter_by(track_id=track_id).scalar().file_path
			# convert absolute file path to relative file path
			track_name = file_path.replace(f"/stringwave/radio/{station}/", "")
			# add track name to list
			queued_track_names.append(track_name)

		subprocess.run(['./scripts/ezstream-queue.sh', station, play_now, *queued_track_names])
		flash('Tracks queued successfully!')
		return redirect(f'/tracks/{station}')


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
		# split passed genres
		genres = request.form.getlist('genres')
		genres = ';'.join(genres)

		# split passed styles
		styles = request.form.getlist('styles')
		styles = ';'.join(styles)

		# extract other configuration values
		decade = request.form['decades']	# decade doesn't work with discogs API, currently useless
		year = request.form['years']
		country = request.form['countries']
		sort_method = request.form['sort_methods']
		sort_order = request.form['order']
		albums_to_find = request.form['number']

		# add new configuration to the database
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

	# if a GET request is submitted to this endpoint, display configuration creation page
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
	# select all configs
	con = sqlite3.connect('webapp/instance/stringwave.db')
	configs = con.cursor().execute('SELECT * FROM config')

	# write to text file
	with open('webapp/static/configs.txt', 'w') as f:
		#[f.write(f'{"|".join(config[1:])}\n') for config in configs.fetchall()]
		for config in configs.fetchall():
			config = [str(item) for item in config[1:]]
			config = '|'.join(config)
			f.write(config + '\n')

	# return download link
	# needs to be fixed returns Not Allowed
	return '<a href="/static/configs.txt" download>Download</a><br><a href="/cogmera/dump_config">Return to Configs</a>'


@app.route('/pipefeeder/list_subs', methods = ['GET'])
@login_required
def listSubs():
	return render_template('subs.html', subs=Subs.query.order_by(func.lower(Subs.channel_name)).all())


@app.route('/pipefeeder/add_sub', methods = ['POST'])
@login_required
def add_sub():
	channel_url = request.form['subscribe']

	# make sure link matches the proper format
	regex = r'^(((https?):\/\/)?(www\.)?youtube\.com)/(c(hannel)?/|@).+$'
	if not re.match(regex, channel_url):
		print(f'{channel_url} is not valid')
		flash('Not a valid YouTube URL')
		return redirect('/pipefeeder/list_subs')

	# get channel's video feed
	feed = get_channel_feed(channel_url)

	# download channel icon
	get_channel_icon(get_channel_url(feed))

	# add new record for channel to database
	new_record = Subs(
		channel_id=get_channel_id(feed), 
		channel_name=get_channel_name(feed), 
		)
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
def del_sub():
	channel_id = request.form['unsubscribe']
	db.session.query(Subs).filter_by(channel_id=channel_id).delete()
	db.session.commit()
	# delete channel icon if it exists
	icon_path = f'webapp/static/images/channel_icons/{channel_id}.jpg'
	if os.path.exists(icon_path):
		os.remove(icon_path)
	return redirect('/pipefeeder/list_subs')


@app.route('/pipefeeder/backup_subs', methods = ['GET'])
@login_required
def backup():
	# get all channel urls from database
	con = sqlite3.connect('webapp/instance/stringwave.db')
	channel_ids = con.cursor().execute('SELECT channel_id FROM subs')

	# write links to text file
	with open('webapp/static/subs.txt', 'w') as f:
		[ f.write(f'{channel_id[0]}\n') for channel_id in channel_ids.fetchall() ]

	# return download link
	return '<a href="/static/subs.txt" download>Download</a><br><a href="/pipefeeder/list_subs">Return to Subs</a>'


@app.route('/pipefeeder/upload_subs', methods = ['GET', 'POST'])
@login_required
def upload_subs():
	# set status to uploading
	with open('webapp/static/upload_status', 'w') as f:
		f.write('uploading')

	file = request.files['subs']
	file_type = file.filename.split('.')[-1]
	logger.debug(f"RECEIVED {file.filename}")

	# make sure file is allowed file type
	# this may not be very secure since it just checks for a file extension
	if file and allowed_file(file.filename):
		logger.debug(f"FILE TYPE {file_type} IS ALLOWED")
		filename = secure_filename(file.filename)
		file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		file.save(file_path)
		logger.debug(f"FILE {file_path} UPLOADED")
		upload.delay(file_path)
		return render_template('upload.html')
	elif not allowed_file(file.filename):
		logger.debug(f"FILE TYPE {file_type} IS NOT ALLOWED")
		flash(f"File {file.filename} is of a disallowed type: {file_type}")
		return redirect("/pipefeeder/list_subs")


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


@app.route('/update_channel_name', methods = ['POST'])
def update_channel_name():
	data = request.form['update-channel-name'].split(';')
	channel_id = data[0]
	new_channel_name = data[1].strip()
	logger.debug(f"UPDATING CHANNEL NAME FOR {channel_id} TO {new_channel_name}")
	channel = db.session.query(Subs).filter_by(channel_id=channel_id).one()
	channel.channel_name = new_channel_name
	db.session.commit()
	return redirect('/pipefeeder/list_subs')


@app.route('/refresh_icon', methods = ['POST'])
def refresh_icon():
	channel_id = request.form['refresh-icon']
	logger.debug(f"REFRESHING ICON FOR CHANNEL WITH ID: {channel_id}")
	get_channel_icon(f"https://youtube.com/channel/{channel_id}")
	logger.debug("ICON REFRESHED SUCCESSFULLY!")
	return redirect('/pipefeeder/list_subs')
