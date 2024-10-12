import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import requests


def test_initial_setup():
    assert os.path.isdir('/stringwave/config')
    assert os.path.isfile('/stringwave/config/ezstream-main.xml')
    assert os.path.isfile('/stringwave/config/ezstream-new.xml')
    assert os.path.isdir('/stringwave/dl_data')
    assert os.path.isfile('/stringwave/dl_data/urls')
    assert os.path.isfile('/stringwave/dl_data/search_queries')
    assert os.path.isfile('/stringwave/webapp/static/upload_status')
    assert os.path.isfile('/stringwave/webapp/static/move_status')
    assert os.path.isfile('/stringwave/webapp/static/now_playing_main')
    assert os.path.isfile('/stringwave/webapp/static/now_playing_new')

def test_admin_account_creation():
    engine = create_engine("sqlite+pysqlite:///webapp/instance/stringwave.db")
    with Session(engine) as session:
        result = session.execute(text("SELECT username FROM users WHERE username='admin';"))
        assert result.all()[0][0] == "admin"

# def test_subscribe():
#     # need to be able to login
#     assert requests.post("http://gateway:8080/pipefeeder/add_sub", data="https://www.youtube.com/@YouTube")