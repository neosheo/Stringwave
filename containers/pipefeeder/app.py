from flask import render_template, request, redirect, flash
from werkzeug.utils import secure_filename
from webapp import *
from sqlalchemy import func
from pipefeeder import *
import sqlite3
import re
from upload import upload


@app.route('/list_subs', methods = ['GET'])
def listSubs():
	return render_template('subs.html', subs=Subs.query.order_by(func.lower(Subs.channel_name)).all())


@app.route('/add_sub', methods = ['POST'])
def addSub():
	channel_url = request.form['subscribe']
	regex = r'^(((https?):\/\/)?(www\.)?youtube\.com)/(c(hannel)?/|@).+$'
	if not re.match(regex, channel_url):
		print(f'{channel_url} is not valid')
		flash('Not a valid YouTube URL')
		return redirect('/list_subs')
	feed = getChannelFeed(channel_url)
	new_record = Subs(channel_id=getChannelId(feed), channel_name=getChannelName(feed), channel_url=getChannelUrl(feed), channel_icon=getChannelIcon(channel_url))
	try:
		db.session.add(new_record)
	except sqlalchemy.exc.IntegrityError:
		print('Duplicate subscription')
		flash('Duplicate subscription')
		return redirect('/list_subs')
	db.session.commit()
	return redirect('/list_subs')


@app.route('/del_sub', methods = ['POST'])
def delSub():
	db.session.query(Subs).filter_by(channel_id=request.form['unsubscribe']).delete()
	db.session.commit()
	return redirect('/list_subs')


@app.route('/backup_subs', methods = ['GET'])
def backup():
	con = sqlite3.connect('pipefeeder/webapp/instance/subs.db')
	urls = con.cursor().execute('SELECT channel_url FROM subs')
	with open('/pipefeeder/backup/subs.txt', 'w') as f:
		[f.write(f'{url[0]}\n') for url in urls.fetchall()]
	return '<a href="/list_subs">Done!</a>'


@app.route('/upload_subs', methods = ['GET', 'POST'])
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


@app.route('/upload_complete', methods = ['GET'])
def upload_complete():
	with open('webapp/static/upload_status', 'w') as f:
		f.write('complete')


@app.route('/upload_status', methods = ['GET'])
def upload_status():
	with open('webapp/static/upload_status', 'r') as f:
		status = f.read()
	json = f'{{ "status": "{status}"}}'
	return json


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False)
