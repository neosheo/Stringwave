#!/bin/bash

link=$1

yt-dlp \
	--parse-metadata '%(uploader)s:%(meta_artist)s' \
	--embed-metadata \
	--replace-in-metadata title '[|%& :;,-/#\*\\"]' '_' \
	--sponsorblock-remove all \
	--sponsorblock-api 'https://api.sponsor.ajay.app/api/' \
	--extract-audio \
	--audio-format opus \
	-o '/stringwave/radio/new/%(title)s.%(ext)s' \
	$link | tee --append /stringwave/logs/pipefeeder.log
