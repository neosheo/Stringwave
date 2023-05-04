#!/bin/bash

filename=$1
search_query=$2
config=$3

yt-dlp \
    ytsearch1:"$search_query" \
    --format '[height<720]' \
    --parse-metadata '%(uploader)s:%(meta_artist)s' \
    --embed-metadata \
    --sponsorblock-remove all \
    --sponsorblock-api 'https://api.sponsor.ajay.app/api/' \
    --extract-audio \
    --audio-format opus \
    -o ./radio/new/"$filename"

python embed_metadata.py ./songs/"$filename".opus "$config"


