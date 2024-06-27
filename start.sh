#!/bin/bash

sqlite3 webapp/instance/stringwave.db <<EOF
DROP TABLE IF EXISTS tracks;
CREATE TABLE IF NOT EXISTS tracks( \
	track_id INTEGER PRIMARY KEY AUTOINCREMENT, \
	title VARCHAR(30), \
	artist VARCHAR(30), \
	track_type VARCHAR(1), \
	config INTEGER, \
	station VARCHAR(4), \
	file_path VARCHAR(300), \
	FOREIGN KEY (config) REFERENCES config (config_id));
EOF

python scripts/build_database.py new main

./scripts/start_radio.sh

uwsgi \
    --socket :3033 \
    --wsgi-file app.py \
    --master \
    --threads 1 \
    --callable app \
    --uid stringwave \
    --gid stringwave
