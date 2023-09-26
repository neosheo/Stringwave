#!/bin/bash

download_log=logs/cogmera_download.log
selection_log=logs/cogmera_selection.log

echo "$(date)" > "$download_log"
echo "$(date)" > "$selection_log"

python -m pip install -U pip | tee --append "$download_log" 2>&1 \
	&& python -m pip install -U yt-dlp --user | tee --append "$download_log" 2>&1

python cogmera.py | tee --append "$selection_log" 2>&1

log=/stringwave/logs/pipefeeder.log

echo "$(date)" > "$log"

python pipefeeder.py | tee --append "$log" 2>&1
sed '/^\/stringwave\//d' logs/pipefeeder.log
	
echo >> "$log"
