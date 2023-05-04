#!/bin/sh

cd /stringwave
./scripts/run_radio.sh

uwsgi \
    --socket :3033 \
    --wsgi-file app.py \
    --threads 2 \
    --callable app \
    --uid stringwave \
    --gid stringwave
