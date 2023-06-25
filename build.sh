#!/bin/bash

echo FLASK_SECRET_KEY=\""$(< /dev/random tr -dc _A-Z-a-z-0-9 | head -c 25;)"\" > .env

NUM_DAILY_DOWNLOADS=5

if [ "$1" = "rebuild" ]
then 
    if [ "$2" = "all" ]
    then
        docker compose down
        docker image rm stringwave
        docker image rm pipefeeder:dev
        docker image rm cogmera:dev
    else
        for image in "${@:2}"
        do
            docker compose down
            docker image rm "$image"
        done
    fi
fi 

docker compose up -d
