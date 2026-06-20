#!/usr/bin/env bash

# source .env
# export POSTGRES_USER
# export POSTGRES_PASSWORD

POSTGRES_USER="$1"
POSTGRES_PASSWORD="$2"
OVERWRITE_ADMIN_USER="$3"

DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/stringwave"

# check for existence of stringwave admin account in database
# if it exists already give user the option to use the old account or create a new one
user_table_exists=$(psql "$DATABASE_URL" -tAc "
	SELECT EXISTS(
		SELECT 1
		FROM information_schema.tables
		WHERE table_schema = 'public'
		AND table_name = 'users'
	);"
)

if [[ "$user_table_exists" == "t" ]]
then
	admin_user_exists=$(psql "$DATABASE_URL" -tAc "
		SELECT EXISTS (
			SELECT 1
			FROM users
			WHERE username = 'admin'
		);"
	)

	# if the admin user exists ask the user if they want to overwrite it with a new password
	if [[ $admin_user_exists == "t" ]]
	then
		if (( OVERWRITE_ADMIN_USER )); then
			echo  "Admin user exists, overwrite? " >&2
			select yn in "Yes" "No"; do
			case $yn in
				Yes )
				echo "Removing old admin account..."; >&2
				# sed -i '/ADMIN_PASSWORD/d' .env;

				psql "$DATABASE_URL" -c "
					DELETE FROM users
					WHERE username = 'admin';
				"
				# ADMIN_PW_MAYBE=ADMIN_PASSWORD;
				echo "Overwrite"
				break;;
				
				No )
				# ADMIN_PW_MAYBE=NULL_PASSWORD;
				echo "Do not overwrite"
				break;;
			esac
			done
		fi
	else
		echo "Create new"
	fi
else
	echo "Create new"
fi

