#!/bin/bash
# clear log and print date
echo $(date) > logs/stringwave.log
echo Running cogmera... >> logs/stringwave.log
python cogmera.py
echo Running pipefeeder... >> logs/stringwave.log
python pipefeeder.py
