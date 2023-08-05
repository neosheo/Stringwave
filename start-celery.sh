#!/bin/bash

celery --app tasks worker --concurrency 1 --loglevel INFO
