#!/bin/bash

download_log=/cogmera/logs/cogmera_download.log
selection_log=/cogmera/logs/cogmera_selection.log

echo "$(date)" > "$download_log"
echo "$(date)" > "$selection_log"

python -m pip install -U pip | tee --append "$download_log" 2>&1 \
 	&& python -m pip install -U yt-dlp | tee --append "$download_log" 2>&1

python /cogmera/run.py | tee --append "$selection_log" 2>&1
