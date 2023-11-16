#!/bin/bash

[ -f webapp/instance/stringwave.db ] || touch webapp/instance/stringwave.db

if ! grep "FLASK_SECRET_KEY" .env > /dev/null;
then
    echo FLASK_SECRET_KEY=\""$(< /dev/random tr -dc _A-Z-a-z-0-9 | head -c 25;)"\" >> .env;
fi

if ! grep "ADMIN_PASSWORD" .env > /dev/null;
then
    echo FLASK_SECRET_KEY=\""$(< /dev/random tr -dc _A-Z-a-z-0-9 | head -c 25;)"\" >> .env;
fi

if ! grep "RABBITMQ_DEFAULT_PASS" .env > /dev/null;
then
    echo RABBITMQ_DEFAULT_PASS=\""$(< /dev/random tr -dc _A-Z-a-z-0-9 | head -c 25;)"\" >> .env;
fi

if ! grep "NUM_DAILY_DOWNLOADS" .env > /dev/null;
then
    echo NUM_DAILY_DOWNLOADS=5 >> .env;
fi

if ! grep "RABBITMQ_DEFAULT_USER" .env > /dev/null;
then
    echo RABBITMQ_DEFAULT_USER=stringwave >> .env;
fi

if [ "$1" = "rebuild" ]
then 
    if [ "$2" = "all" ]
    then
        docker compose down
        docker image rm stringwave
        docker image rm stringwave-celery
    else
        for image in "${@:2}"
        do
            docker compose down
            docker image rm "$image"
        done
    fi
fi 

docker compose up -d

unset NUM_DAILY_DOWNLOADS
unset FLASK_SECRET_KEY
unset RABBITMQ_DEFAULT_USER
unset RABBITMQ_DEFAULT_PASS
unset ADMIN_PASSWORD
