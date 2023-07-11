#!/bin/bash

filename=$1
artist=$2
search_query=$3
config=$4

yt-dlp \
    ytsearch1:"$search_query" \
    --format '[height<720]' \
    --sponsorblock-remove all \
    --sponsorblock-api 'https://api.sponsor.ajay.app/api/' \
    --extract-audio \
    --audio-format opus \
    -o ./radio/new/"$filename" | tee --append /stringwave/logs/cogmera_download.log

python scripts/embed_metadata.py ./radio/new/"$filename".opus "$artist" "$config"


