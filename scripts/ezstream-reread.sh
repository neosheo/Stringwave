#!/bin/bash

station=$1

cd /stringwave/radio/"$station"

python /stringwave/scripts/remove_whitespaces.py new

find /stringwave/radio -name "*.opus" > /stringwave/radio/"$station"/.playlist

ezpid="$(cat /stringwave/.pid)"

if ps h --pid $ezpid
then
    kill -1 $ezpid
else
    ./scripts/ezstream.sh
fi
