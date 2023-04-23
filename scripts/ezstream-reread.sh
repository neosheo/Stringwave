#!/bin/bash

cd /stringwave/radio && python remove_whitespaces.py 

./convert.sh

find /stringwave/radio -name "*.opus" > /stringwave/radio/.playlist
