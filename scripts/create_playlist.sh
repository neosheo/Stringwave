#!/usr/bin/env bash

station=$1
radio_path=/stringwave/radio/$station
playlist=$radio_path/.playlist

# create playlist file if it doesn't exist
if ! [ -f $playlist ]; then
    touch $playlist
fi

# clear playlist in case it already has data
> $playlist

# write the list of files in the radio directory to the playlist file
# shuffle the tracks into a random order
# and convert absolute paths to relative paths
find $radio_path -name "*.opus" | shuf | sed "s|/stringwave/radio/$station|.|g" >> $playlist
