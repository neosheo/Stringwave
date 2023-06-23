from webapp import celery_app
import requests
import os
import subprocess


@celery_app.task
def move_track(track):
	if track[-5:] != '.opus':
		track = f'{track}.opus'
	subprocess.run(['mv', f'/stringwave/radio/new/{track}', f'/stringwave/radio/main/{track}'])
	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'new'])
	subprocess.run([f'{os.getcwd()}/scripts/ezstream-reread.sh', 'main'])
	requests.get('http://gateway/move_complete')