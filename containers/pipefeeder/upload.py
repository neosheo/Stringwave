from webapp import celery_app
from pipefeeder import populateDb
import requests


@celery_app.task
def upload(file_path):
	populateDb(file_path)
	requests.get('http://localhost:80/upload_complete')
