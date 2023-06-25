#!/bin/bash

sqlite3 webapp/instance/radio.db <<EOF
CREATE TABLE IF NOT EXISTS tracks(track_id INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR(30), artist VARCHAR(30), config INTEGER, station VARCHAR(4));
EOF

python scripts/build_database.py new
python scripts/build_database.py main

curl --user guest:guest \
    -H "content-type:application/json" \
    -X PUT http://rabbitmq:15672/api/vhosts/stringwave/

./scripts/run_radio.sh

session="celery"
window=0
tmux new-session -d -s $session
tmux rename-window -t $session:$window $session
tmux send-keys -t $session:$window "celery --app tasks worker -n stringwave@%h --loglevel INFO" C-m

uwsgi \
    --socket :3033 \
    --wsgi-file app.py \
    --master \
    --threads 2 \
    --callable app \
    --uid stringwave \
    --gid stringwave
