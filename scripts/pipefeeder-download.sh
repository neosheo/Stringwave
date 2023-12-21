#!/bin/bash

link=$1

yt-dlp \
	--verbose \
	--no-simulate \
	--match-filter "title !~= (?i).*(#shorts|(\[|\()?full_(album|ep)(\]|\))?).*" \
	--parse-metadata '%(uploader)s:%(meta_artist)s' \
	--embed-metadata \
	--embed-thumbnail \
	--replace-in-metadata title '[|% :/#\*\\"!]' '_' \
	--sponsorblock-remove all \
	--sponsorblock-api 'https://api.sponsor.ajay.app/api/' \
	--extract-audio \
	--audio-format opus \
	-o '/stringwave/radio/new/%(title)s.%(ext)s' \
	--print filename \
	$link | tee --append /stringwave/logs/pipefeeder.log
