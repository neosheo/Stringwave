#!/bin/bash
# clear log and print date
echo $(date) > logs/stringwave.log
pip install --upgrade yt-dlp
python cogmera.py
python pipefeeder.py
