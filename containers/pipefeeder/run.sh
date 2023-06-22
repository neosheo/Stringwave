#!/bin/bash

log=/pipefeeder/logs/pipefeeder.log

echo "$(date)" > "$log"

python -m pip install -U pip | tee --append "$log" 2>&1 \
 	&& python -m pip install -U yt-dlp --user | tee --append "$log" 2>&1

python pipefeeder.py | tee --append "$log" 2>&1
	
echo >> "$log"
