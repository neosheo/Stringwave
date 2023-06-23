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

find /stringwave/radio -name "*.opus" > /stringwave/radio/"$station"/.playlist

ezpid="$(cat /stringwave/.pid-$station)"

# checks if station is run and starts it if it wasn't running, otherwise triggers a reread
if ps h --pid $ezpid
then
    kill -1 $ezpid
else
    /stringwave/scripts/ezstream.sh "$station"
fi
