from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from celery import Celery, Task


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
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{os.getcwd()}/webapp/instance/radio.db'
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config.from_mapping(
    CELERY=dict(
        broker_url='pyamqp://guest@rabbitmq//',
        backend_url='pyamqp://guest@rabbitmq//',
        task_ignore_result=True
    )
)
celery_app = celery_init_app(app)
db = SQLAlchemy(app)


class Tracks(db.Model):
	track_id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(30))
	artist = db.Column(db.String(30))
	config = db.Column(db.Integer)
	station = db.Column(db.String(4))

with app.app_context():
	db.create_all()
