#!/usr/bin/env bash

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
cp config_examples/* config
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
	webapp/static/now_playing_new \

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

# create database if one is not already provided
[ -f webapp/instance/stringwave.db ] || touch webapp/instance/stringwave.db

if ! grep DISCOGS_PERSONAL_ACCESS_TOKEN .env > /dev/null;
then
	read -p "Enter discogs personal access token: " access_token
	echo DISCOGS_PERSONAL_ACCESS_TOKEN=\"$access_token\" >> .env
fi

# check for existence of stringwave admin account in database
# if it exists already give user the option to use the old account or create a new one
table_exists=$(sqlite3 webapp/instance/stringwave.db "SELECT EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='users');")
if [[ "$table_exists" -eq 1 ]]
then
	if sqlite3 webapp/instance/stringwave.db "SELECT EXISTS(SELECT 1 FROM users WHERE username='admin');" > /dev/null
	then
    	echo  "Admin user exists, overwrite? "
	    select yn in "Yes" "No"; do
		case $yn in
		    Yes )
			echo "Removing old admin account...";
    	    sed -i '/ADMIN_PASSWORD/d' .env;
        	sqlite3 webapp/instance/stringwave.db "DELETE FROM users WHERE username='admin';";
			ADMIN_PW_MAYBE=ADMIN_PASSWORD;
			break;;
        	No )
			ADMIN_PW_MAYBE=NULL_PASSWORD;
			break;;
		esac
	    done
	else
		ADMIN_PW_MAYBE=ADMIN_PASSWORD;
	fi
else
	ADMIN_PW_MAYBE=ADMIN_PASSWORD;
fi

for env_var in FLASK_SECRET_KEY RABBITMQ_DEFAULT_PASS $ADMIN_PW_MAYBE
do
    if ! grep "$env_var" .env > /dev/null;
    then
        echo "$env_var"=\""$(< /dev/random tr -dc _A-Z-a-z-0-9 | head -c 25;)"\" >> .env;
    fi
done
sed -i '/NULL_PASSWORD/d' .env

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

docker compose up -d

unset NUM_DAILY_DOWNLOADS
unset FLASK_SECRET_KEY
unset RABBITMQ_DEFAULT_USER
unset RABBITMQ_DEFAULT_PASS
unset ADMIN_PASSWORD