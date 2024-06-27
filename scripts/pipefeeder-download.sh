#!/bin/bash

link=$1

yt-dlp \
	--verbose \
	--quiet \
	--no-simulate \
	--match-filter "title !~= (?i).*(#shorts|(\[|\()?full_(album|ep)(\]|\))?).*" \
	--parse-metadata '%(uploader)s:%(meta_artist)s' \
	--embed-metadata \
	--replace-in-metadata title '[|% :/#\*\\"!]' '_' \
	--sponsorblock-remove all \
	--sponsorblock-api 'https://api.sponsor.ajay.app/api/' \
	--postprocessor-args "Metadata:-vn" \
	--embed-thumbnail \
	--extract-audio \
	--audio-format opus \
	-F --extractor-args "youtube:player_client=web" \
	-o '/stringwave/radio/new/%(title)s.%(ext)s' \
	--print filename \
	$link
