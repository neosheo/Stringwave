#!/bin/bash

celery --app upload worker --loglevel INFO &

uwsgi \
    --socket :3031 \
    --wsgi-file app.py \
    --master \
    --threads 2 \
    --callable app \
    --uid pipefeeder \
    --gid pipefeeder
