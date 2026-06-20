#!/usr/bin/env bash

# make sure user is in the main directory and not build
if [[ "$(pwd)" == *"/build" ]]; then
    cd ..
fi

# create needed files and directories
mkdir -p radio/new \
	radio/main \
	config \
	dl_data \
	logs \
	webapp/instance \
	webapp/static/images/channel_icons \
	webapp/static/uploads

touch .env \
	dl_data/pf_download_status \
	dl_data/cm_download_status \
	dl_data/urls \
	dl_data/search_queries \
	logs/stringwave.log \
	logs/pipefeeder.log \
	logs/cogmera.log \
	webapp/static/upload_status \
	webapp/static/move_status \
	webapp/static/now_playing_main \
	webapp/static/now_playing_new

# copy config examples into the config to write passwords into
cp config_examples/* config

# set source password for ezstream and icecast
PASSWORD="$(< /dev/random tr -dc _A-Z-a-z-0-9 | head -c 25;)"
sed -i "s/<password><\/password>/<password>$PASSWORD<\/password>/g" config/ezstream-main.xml
sed -i "s/<password><\/password>/<password>$PASSWORD<\/password>/g" config/ezstream-new.xml
sed -i "s/<source-password><\/source-password>/<source-password>$PASSWORD<\/source-password>/g" config/icecast.xml

# set relay and admin passwords for icecast
for user in relay admin
do
    PASSWORD="$(< /dev/random tr -dc _A-Z-a-z-0-9 | head -c 25;)"
    sed -i "s/<$user-password><\/$user-password>/<$user-password>$PASSWORD<\/$user-password>/g" config/icecast.xml
done
unset PASSWORD

# write needed environment variables
if ! grep "POSTGRES_USER" .env > /dev/null;
then
    echo POSTGRES_USER=stringwave >> .env
fi

# write default setting of whether to prompt user to overwrite admin user settings
# default is 0 which means it will leave existing admin user if admin user exists
# set to 1 if you want it to prompt for overwrite each time if admin user exists
if ! grep "OVERWRITE_ADMIN_USER" .env > /dev/null;
then
    echo OVERWRITE_ADMIN_USER=0 >> .env
fi

if ! grep DISCOGS_PERSONAL_ACCESS_TOKEN .env > /dev/null;
then
	read -p "Enter discogs personal access token: " access_token
	echo DISCOGS_PERSONAL_ACCESS_TOKEN=\"$access_token\" >> .env
fi

for env_var in FLASK_SECRET_KEY RABBITMQ_DEFAULT_PASS POSTGRES_PASSWORD
do
    if ! grep "$env_var" .env > /dev/null;
    then
        echo "$env_var"=\""$(< /dev/random tr -dc _A-Z-a-z-0-9 | head -c 25;)"\" >> .env;
    fi
done

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
        docker image rm stringwave-icecast
    else
        for image in "${@:2}"
        do
            docker compose down
            docker image rm "$image"
        done
    fi
fi 

docker compose up -d --no-deps postgres
# wait until healthy
until [ "$(docker inspect -f '{{.State.Health.Status}}' stringwave-postgres)" = "healthy" ]
do
    sleep 1
done

# extract postgres credentials
source .env
export POSTGRES_USER
export POSTGRES_PASSWORD
export OVERWRITE_ADMIN_USER

# check for admin user and add if it doesn't exist
# trim any newline characters

ADMIN_PW_SETTING=$(docker compose exec postgres /scripts/database_user_init.sh "$POSTGRES_USER" "$POSTGRES_PASSWORD" "$OVERWRITE_ADMIN_USER"| tr -d '\r\n')

# create cogmera database
docker compose exec postgres dropdb -U stringwave cogmera
docker compose exec postgres psql -U stringwave -d postgres -c "CREATE DATABASE cogmera;"
docker compose exec -T postgres psql -U stringwave -d cogmera < build/cogmera.sql
docker compose down postgres

# set admin password if needed
if [[ "$ADMIN_PW_SETTING" == "Overwrite" ]]
    then
        sed -i '/^ADMIN_PASSWORD=/d' .env;
		echo "ADMIN_PASSWORD=\"$(< /dev/random tr -dc _A-Z-a-z-0-9 | head -c 25;)\"" >> .env;
elif [[ "$ADMIN_PW_SETTING" == "Create new" ]]
    then
        if ! grep "ADMIN_PASSWORD=" .env > /dev/null;
            then
                echo "ADMIN_PASSWORD=\"$(< /dev/random tr -dc _A-Z-a-z-0-9 | head -c 25;)\"" >> .env;
        fi
fi

docker compose up -d

unset NUM_DAILY_DOWNLOADS
unset FLASK_SECRET_KEY
unset RABBITMQ_DEFAULT_USER
unset RABBITMQ_DEFAULT_PASS
unset ADMIN_PASSWORD

# allow user to immediately follow the logs of a container
for (( i=1; i<=$#; i++ )); do
    arg="${!i}"
    if [[ "$arg" == "-f" ]] || [[ "$arg" == "--follow" ]]; then
        next_arg_index=$((i + 1))
        image_name="${!next_arg_index}"
        if [[ "$image_name" != "stringwave" ]]; then
            image_name="stringwave-${image_name}"
        fi
        # if user wants to follow stringwave or celery containers, follow the log file
        # otherwise follow container log
        if [[ "$image_name" != "stringwave" ]] || [[ $"image_name" != "stringwave-celery" ]]; then
            docker logs -f "$image_name" 
        else
            docker exec "$image_name" tail -f /stringwave/logs/stringwave.log
        fi
        break
    fi
done