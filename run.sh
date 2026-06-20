#!/bin/bash
# clear log and print date
echo $(date) > logs/stringwave.log

# run cogmera and pipefeeder
echo Running cogmera... >> logs/stringwave.log
python cogmera.py
echo Running pipefeeder... >> logs/stringwave.log
python pipefeeder.py