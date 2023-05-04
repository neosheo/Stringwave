from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.config['SQLALCHEMY_BINDS'] = {
	'main': f'sqlite:////{os.getcwd()}/webapp/instance/cogmera.db',
	'conf': f'sqlite:////{os.getcwd()}/webapp/instance/configs.db'
}
db = SQLAlchemy(app)


class Genres(db.Model):
		__bind_key__ = 'main'
		genre_id = db.Column(db.Integer, primary_key=True)
		genre = db.Column(db.String(21))


class Styles(db.Model):
        __bind_key__ = 'main'
        style_id = db.Column(db.Integer, primary_key=True)
        style = db.Column(db.String(30))


class Countries(db.Model):
		__bind_key__ = 'main'
		country_id = db.Column(db.Integer, primary_key=True)
		country = db.Column(db.String(45))


class Decades(db.Model):
		__bind_key__ = 'main'
		decade_id = db.Column(db.Integer, primary_key=True)
		decade = db.Column(db.String(4))


class Years(db.Model):
		__bind_key__ = 'main'
		year_id = db.Column(db.Integer, primary_key=True)
		year = db.Column(db.String(4))


class SortMethods(db.Model):
		__bind_key__ = 'main'
		sort_method_id = db.Column(db.Integer, primary_key=True)
		sort_method = db.Column(db.String(1))


class Config(db.Model):
        __bind_key__ = 'conf'
        config_id = db.Column(db.Integer, primary_key=True)
        genres = db.Column(db.String(21))
        styles = db.Column(db.String(30))
        decade = db.Column(db.String(4))
        year = db.Column(db.String(4))
        country = db.Column(db.String(45))
        sort_method = db.Column(db.String(1))
        sort_order = db.Column(db.String(4))
        albums_to_find = db.Column(db.Integer)


with app.app_context():
	db.create_all('main')
	db.create_all('conf')
