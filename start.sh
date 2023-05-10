#!/bin/bash

sqlite3 webapp/instance/radio.db <<EOF
CREATE TABLE radio_new(track_id INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR(30), artist VARCHAR(30), config INTEGER);
EOF

python scripts/build_database new

./scripts/run_radio.sh

uwsgi \
    --socket :3033 \
    --wsgi-file app.py \
    --threads 2 \
    --callable app \
    --uid stringwave \
    --gid stringwave
