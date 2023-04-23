#!/bin/bash

for file in $(find /stringwave/radio -name "*.mp3")
do
	filename=$(basename "$file" .mp3)
	ffmpeg -i $file -c:a libopus $filename.opus && rm $file
done
