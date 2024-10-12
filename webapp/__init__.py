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
db_directory = f'sqlite:////{os.getcwd()}/webapp/instance'
radio_path = '/stringwave/radio'
log_path = 'logs'

log_level = logging.DEBUG

def setup_logger(name, level=logging.INFO):
    log_file = f'{log_path}/{name}.log'
    handler = logging.FileHandler(log_file)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

pf_logger = setup_logger('pipefeeder', level=log_level)
cm_logger = setup_logger('cogmera')
sw_logger = setup_logger('stringwave')

# only allow backups that have .txt extension
BACKUP_LOCATION = f'{os.getcwd()}/webapp/static/uploads'
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
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'foreign_keys': 'ON'}
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
	channel_name = db.Column(db.String(35), nullable=False)
	video_title_regex = db.Column(db.String(35), nullable=True)
	regex_type = db.Column(db.String(12), nullable=True)


class Tracks(db.Model):
	__bind_key__ = 'main'
	track_id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	artist = db.Column(db.String(30), nullable=False)
	track_type = db.Column(db.String(1), nullable=False)
	config = db.Column(db.Integer, db.ForeignKey('config.config_id'), nullable=False)
	station = db.Column(db.String(4), nullable=False)
	file_path = db.Column(db.String(300), nullable=False)
	config_rel = db.relationship('Config', backref='tracks', lazy=True, uselist=False)


class Config(db.Model):
	__bind_key__ = 'main'
	config_id = db.Column(db.Integer, primary_key=True)
	genres = db.Column(db.String(21), nullable=False)
	styles = db.Column(db.String(30), nullable=False)
	decade = db.Column(db.String(4), nullable=False)
	year = db.Column(db.String(4), nullable=False)
	country = db.Column(db.String(45), nullable=False)
	sort_method = db.Column(db.String(1), nullable=False)
	sort_order = db.Column(db.String(4), nullable=False)
	albums_to_find = db.Column(db.Integer, nullable=False)


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
