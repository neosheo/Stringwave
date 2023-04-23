from flask import render_template, request, redirect
from webapp import *
from stringwave import *
import subprocess
import re


@app.route('/')
def radio():
	return render_template('index.html', tracks=Tracks.query.order_by(Tracks.track_id).all())


@app.route('/download', methods = ['POST'])
def download():
	command = request.form['command']
	regex = r'^yt-dlp(?!.*([&]{1,2}|[\|]{1,2}|;)).*$'
	if not re.match(regex, command):
		return redirect('/')
	subprocess.run([command])

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
