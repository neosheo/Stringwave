#!/bin/bash

station=$1

cd /stringwave/radio/"$station"

if (find -name "*.opus" | grep .)
then
    python /stringwave/scripts/remove_whitespaces.py "$station"
    find . -name "*.opus" > .playlist
    
	for i in 1 2 3 4 5
		do ezstream -rv -p /stringwave/.pid-$station -c /stringwave/config/ezstream-$station.xml
	done

else
    echo No tracks found
fi
