#!/bin/bash

filename=$1
title=$2
artist=$3
search_query=$4
config=$5

yt-dlp \
	--match-filter "title !~= (?i)(#shorts|(\[|\()?full (album|ep)(\]|\))?)" \
    ytsearch1:"$search_query" \
    --format '[height<720]' \
    --sponsorblock-remove all \
    --sponsorblock-api 'https://api.sponsor.ajay.app/api/' \
    --extract-audio \
    --audio-format opus \
    -o ./radio/new/"$filename" | tee --append /stringwave/logs/cogmera_download.log

python scripts/embed_metadata.py /stringwave/radio/new/"$filename".opus "$title" "$artist" "$config"


