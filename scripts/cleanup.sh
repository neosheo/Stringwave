#!/bin/bash

python scripts/clean_radio.py "new"

# source .env
# export POSTGRES_USER
# export POSTGRES_PASSWORD

DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/stringwave"

# delete duplicate entries in database
#sqlite3 webapp/instance/stringwave.db <<EOF
psql "$DATABASE_URL" <<EOF
DELETE FROM tracks
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
		FROM tracks
        GROUP BY title, artist, station
	)
	AND (title, artist, station) IN (
		SELECT title, artist, station
		FROM tracks
		GROUP BY title, artist, station
		HAVING COUNT(*) > 1
	);
EOF
# unset POSTGRES_USER POSTGRES_PASSWORD
