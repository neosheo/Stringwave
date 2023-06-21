#!/bin/bash

station=$1

cd /stringwave/radio/"$station"

if [ -z "$(ls)" ]
then
    rm .playlist
    exit
fi

python /stringwave/scripts/remove_whitespaces.py new

find /stringwave/radio -name "*.opus" > /stringwave/radio/"$station"/.playlist

ezpid="$(cat /stringwave/.pid-$station)"

if ps h --pid $ezpid
then
    kill -1 $ezpid
else
    /stringwave/scripts/ezstream.sh "$station"
fi
