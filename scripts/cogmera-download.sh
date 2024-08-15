#!/bin/bash

filename=$1
title=$2
artist=$3
search_query=$4
config=$5

yt-dlp \
	ytsearch1:"$search_query" \
	--verbose \
	--quiet \
	--no-simulate \
	--match-filter "title !~= (?i)(#shorts|(\[|\()?full (album|ep)(\]|\))?)" \
	--sponsorblock-remove all \
	--embed-metadata \
	--embed-thumbnail \
	--postprocessor-args "Metadata:-vn" \
	--sponsorblock-api 'https://api.sponsor.ajay.app/api/' \
	--extract-audio \
	--audio-format opus \
	--format bestaudio \
	-o /stringwave/radio/new/"$filename"

python scripts/embed_metadata.py /stringwave/radio/new/"$filename".opus "$title" "$artist" "$config"


