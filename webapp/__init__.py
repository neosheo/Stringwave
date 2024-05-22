from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from wtforms import StringField, PasswordField, SubmitField
import os
from celery import Celery, Task
import logging


# rabbitmq credentials
rabbitmq_user = os.getenv('RABBITMQ_DEFAULT_USER')
rabbitmq_pass = os.getenv('RABBITMQ_DEFAULT_PASS')

# PATHS
cogmera_log = '/stringwave/logs/cogmera_download.log'
pipefeeder_log = '/stringwave/logs/pipefeeder.log'
db_directory = f'sqlite:////{os.getcwd()}/webapp/instance'
radio_path = '/stringwave/radio'

# set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
	filename="logs/stringwave.log",
	encoding="utf-8",
	level=logging.DEBUG
)

# only allow backups that have .txt extension
BACKUP_LOCATION = f'{os.getcwd()}/webapp/static'
ALLOWED_EXTENSIONS = {'txt'}
def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def celery_init_app(app: Flask) -> Celery:
	class FlaskTask(Task):
		def __call__(self, *args: object, **kwargs: object) -> object:
			with app.app_context():
				return self.run(*args, **kwargs)
	celery_app = Celery(app.name, task_cls=FlaskTask)
	celery_app.config_from_object(app.config['CELERY'])
	celery_app.set_default()
	app.extensions['celery'] = celery_app
	return celery_app


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_BINDS'] = {
	'discogs': f'{db_directory}/cogmera.db',
	'main': f'{db_directory}/stringwave.db'
}
app.config['UPLOAD_FOLDER'] = BACKUP_LOCATION
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config.from_mapping(
	CELERY=dict(
		broker_url=f'pyamqp://{rabbitmq_user}@rabbitmq/',
		backend_url=f'pyamqp://{rabbitmq_user}@rabbitmq/',
		broker_password=rabbitmq_pass,
		task_ignore_result=True,
		broker_connection_retry_on_startup=True,
		worker_cancel_long_running_tasks_on_connection_loss=True
	)
)

celery_app = celery_init_app(app)
db = SQLAlchemy(app)
flask_bcrypt = Bcrypt(app)


def create_admin_user(bcrypt_obj):
	password = os.getenv('ADMIN_PASSWORD')
	hashed_pw = bcrypt_obj.generate_password_hash(password)
	if db.session.query(Users).filter(Users.user_id == 1).first() is None:
		admin_user = Users(
			user_id=1,
			username="admin",
			password=hashed_pw,
		)
		db.session.add(admin_user)
		db.session.commit()


class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')


class Users(db.Model):
	__bind_key__ = 'main'
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, nullable=False, unique=True)
	password = db.Column(db.String, nullable=False)
	def is_authenticated(self):
		return self.authenticated
	def is_active(self):
		return True
	def get_id(self):
		return self.username
	def is_anonymous(self):
		return False


login_manager = LoginManager()
login_manager.init_app(app)


class Subs(db.Model):
	__bind_key__ = 'main'
	channel_id = db.Column(db.String(24), primary_key=True)
	channel_name = db.Column(db.String(35))
	channel_url = db.Column(db.String(300))
	channel_icon = db.Column(db.String(300))


class Tracks(db.Model):
	__bind_key__ = 'main'
	track_id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100))
	artist = db.Column(db.String(30))
	config = db.Column(db.Integer)
	station = db.Column(db.String(4))
	file_path = db.Column(db.String(300))


class Config(db.Model):
	__bind_key__ = 'main'
	config_id = db.Column(db.Integer, primary_key=True)
	genres = db.Column(db.String(21))
	styles = db.Column(db.String(30))
	decade = db.Column(db.String(4))
	year = db.Column(db.String(4))
	country = db.Column(db.String(45))
	sort_method = db.Column(db.String(1))
	sort_order = db.Column(db.String(4))
	albums_to_find = db.Column(db.Integer)


class Genres(db.Model):
	__bind_key__ = 'discogs'
	genre_id = db.Column(db.Integer, primary_key=True)
	genre = db.Column(db.String(21))


class Styles(db.Model):
	__bind_key__ = 'discogs'
	style_id = db.Column(db.Integer, primary_key=True)
	style = db.Column(db.String(30))


class Countries(db.Model):
	__bind_key__ = 'discogs'
	country_id = db.Column(db.Integer, primary_key=True)
	country = db.Column(db.String(45))


class Decades(db.Model):
	__bind_key__ = 'discogs'
	decade_id = db.Column(db.Integer, primary_key=True)
	decade = db.Column(db.String(4))


class Years(db.Model):
	__bind_key__ = 'discogs'
	year_id = db.Column(db.Integer, primary_key=True)
	year = db.Column(db.String(4))


class SortMethods(db.Model):
	__bind_key__ = 'discogs'
	sort_method_id = db.Column(db.Integer, primary_key=True)
	sort_method = db.Column(db.String(1))


with app.app_context():
	db.create_all('main')
	db.create_all('discogs')
	create_admin_user(flask_bcrypt)
