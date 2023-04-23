#!/bin/bash

cd radio && python remove_whitespaces.py

find . -name "*.opus" > .playlist

ezstream -rv -p .pid -c /stringwave/config/ezstream.xml

