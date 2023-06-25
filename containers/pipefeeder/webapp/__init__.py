from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from celery import Celery, Task


BACKUP_LOCATION = f'{os.getcwd()}/backup'
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
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{os.getcwd()}/webapp/instance/subs.db'	
app.config['UPLOAD_FOLDER'] = BACKUP_LOCATION
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config.from_mapping(
    CELERY=dict(
        broker_url='pyamqp://guest@rabbitmq/pipefeeder',
        backend_url='pyamqp://guest@rabbitmq/pipefeeder',
        task_ignore_result=True
    )
)
celery_app = celery_init_app(app)
db = SQLAlchemy(app)


class Subs(db.Model):
         channel_id = db.Column(db.String(24), primary_key=True)
         channel_name = db.Column(db.String(35))
         channel_url = db.Column(db.String(300))
         channel_icon = db.Column(db.String(300))


with app.app_context():
	db.create_all()
