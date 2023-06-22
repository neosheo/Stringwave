#!/bin/bash

station=$1

cat /stringwave/.pid-$station | xargs kill -USR1