#!/bin/bash
# clear log and print date
echo $(date) > logs/stringwave.log
python cogmera.py
python pipefeeder.py
