#!/bin/bash

log=/cogmera/cogmera.log

echo "$(date)" > "$log"

python -m pip install -U pip | tee --append "$log" 2>&1 \
 	&& python -m pip install -U yt-dlp | tee --append "$log" 2>&1

python /cogmera/run.py | tee "$log" 2>&1

echo >> "$log"
