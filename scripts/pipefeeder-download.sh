#!/bin/bash

link=$1

yt-dlp \
	--verbose \
	--no-simulate \
	--match-filter "title !~= (?i)(#shorts|(\[|\()?full (album|ep)(\]|\))?)" \
	--format '[height<720]' \
	--parse-metadata '%(uploader)s:%(meta_artist)s' \
	--embed-metadata \
	--replace-in-metadata title '[|% :;,-/#\*\\"!]' '_' \
	--sponsorblock-remove all \
	--sponsorblock-api 'https://api.sponsor.ajay.app/api/' \
	--extract-audio \
	--audio-format opus \
	-o '/stringwave/radio/new/%(title)s.%(ext)s' \
	--print filename \
	$link | tee --append /stringwave/logs/pipefeeder.log