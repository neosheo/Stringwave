#!/bin/bash

# sqlite3 webapp/instance/stringwave.db <<EOF
# DROP TABLE IF EXISTS tracks;
# CREATE TABLE IF NOT EXISTS tracks( \
# 	track_id INTEGER PRIMARY KEY AUTOINCREMENT, \
# 	title VARCHAR(30), \
# 	artist VARCHAR(30), \
# 	track_type VARCHAR(1), \
# 	config INTEGER, \
# 	station VARCHAR(4), \
# 	file_path VARCHAR(300), \
# 	discogs_link VARCHAR(300), \
# 	FOREIGN KEY (config) REFERENCES config (config_id));
# EOF

# source .env
# export POSTGRES_USER
# export POSTGRES_PASSWORD

DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/stringwave"

psql "$DATABASE_URL" <<EOF
DROP TABLE IF EXISTS tracks;
EOF

# CREATE TABLE tracks (
#     track_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
#     title VARCHAR(30),
#     artist VARCHAR(30),
#     track_type VARCHAR(1),
#     config INTEGER,
#     station VARCHAR(4),
#     file_path VARCHAR(300),
#     discogs_link VARCHAR(300),
#     FOREIGN KEY (config) REFERENCES config (config_id)
# );

#unset POSTGRES_USER POSTGRES_PASSWORD

python -m scripts.build_database new main

./scripts/create_playlist.sh "new"
./scripts/create_playlist.sh "main"

./scripts/start_radio.sh

uwsgi \
    --socket :3033 \
    --wsgi-file app.py \
    --master \
    --threads 1 \
    --callable app \
    --uid stringwave \
    --gid stringwave
