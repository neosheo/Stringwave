#!/bin/bash

sqlite3 webapp/instance/radio.db <<EOF
CREATE TABLE tracks(track_id INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR(30), artist VARCHAR(30), config INTEGER, station VARCHAR(4));
EOF

python scripts/build_database.py new
python scripts/build_database.py main

./scripts/run_radio.sh

uwsgi \
    --socket :3033 \
    --wsgi-file app.py \
    --threads 2 \
    --callable app \
    --uid stringwave \
    --gid stringwave
