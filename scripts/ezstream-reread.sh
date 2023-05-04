#!/bin/bash

station=$1

cd /stringwave/radio/"$station"

python /stringwave/scripts/remove_whitespaces.py 

find /stringwave/radio -name "*.opus" > /stringwave/radio/"$station"/.playlist

ezpid = "$(cat /stringwave/.pid)"

if ps h --pid $ezpid
then
    kill -1 $ezpid
else
    ./ezstream.sh
fi
