#!/bin/bash

station=$1

cd /stringwave/radio/"$station"

# deletes the playlist file if station is empty
if [ -z "$(ls)" ]
then
    rm .playlist
    exit
fi

python /stringwave/scripts/remove_whitespaces.py new

find /stringwave/radio/"$station" -name "*.opus" > /stringwave/radio/"$station"/.playlist

if [ -f /stringwave/.pid-$station ]
then
	ezpid="$(cat /stringwave/.pid-$station)"
	# checks if station is running and starts it if it wasn't running, otherwise triggers a reread
	if ps h --pid $ezpid
	then
	    kill -SIGHUP $ezpid
	else
	    /stringwave/scripts/ezstream.sh "$station"
	fi

else
	/stringwave/scripts/ezstream.sh "$station"
fi
