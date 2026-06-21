#!/bin/bash


# remove existing tracks table
DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/stringwave"
psql "$DATABASE_URL" <<EOF
DROP TABLE IF EXISTS tracks;
EOF

# initialize the database, creates tracks table, creates missing tables and admin user if needed
python -m scripts.build_database new main

# create the playlist files for both stations
./scripts/create_playlist.sh "new"
./scripts/create_playlist.sh "main"

# turn the radios on
./scripts/start_radio.sh

# start the app
uwsgi \
    --socket :3033 \
    --wsgi-file app.py \
    --master \
    --threads 1 \
    --callable app \
    --uid stringwave \
    --gid stringwave
