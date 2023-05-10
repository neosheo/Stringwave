from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{os.getcwd()}/webapp/instance/radio.db'
db = SQLAlchemy(app)

class Tracks(db.Model):
	track_id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(30))
	artist = db.Column(db.String(30))
	config = db.Column(db.Integer)

with app.app_context():
	db.create_all()
