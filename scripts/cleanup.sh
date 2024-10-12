#!/bin/bash

python scripts/clean_radio.py "new"

# delete duplicate entries in database
sqlite3 webapp/instance/stringwave.db <<EOF
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
