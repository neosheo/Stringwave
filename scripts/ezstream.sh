#!/bin/bash

station=$1

cd /stringwave/radio/"$station"

python /stringwave/scripts/remove_whitespaces.py "$station"

find . -name "*.opus" > .playlist

ezstream -rv -p /stringwave/.pid -c /stringwave/config/ezstream.xml

