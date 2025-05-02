#!/bin/bash

station=$1

cd /stringwave/radio/"$station"

for i in 1 2 3 4 5
    do ezstream -rv -p /stringwave/.pid-$station -c /stringwave/config/ezstream-$station.xml
done