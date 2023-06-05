#!/bin/bash

echo FLASK_SECRET_KEY=\""$(< /dev/random tr -dc _A-Z-a-z-0-9 | head -c${1:-25}; echo;)"\" > .env

docker compose up -d