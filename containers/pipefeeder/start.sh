#!/bin/bash

curl --user guest:guest \
    -H "content-type:application/json" \
    -X PUT http://rabbitmq:15672/api/vhosts/pipefeeder/

session="celery"
window=0
tmux new-session -d -s $session
tmux rename-window -t $session:$window $session
tmux send-keys -t $session:$window "celery --app upload worker -n pipefeeder@%h --loglevel INFO" C-m

uwsgi \
    --socket :3031 \
    --wsgi-file app.py \
    --master \
    --threads 2 \
    --callable app \
    --uid pipefeeder \
    --gid pipefeeder
