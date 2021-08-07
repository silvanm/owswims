#!/bin/bash

python ./manage.py migrate --no-input

gunicorn \
 --bind 0.0.0.0:8000 \
 --worker-class=uvicorn.workers.UvicornWorker \
 --worker-connections=1000 \
 --access-logfile - \
 --error-logfile - \
 --env DJANGO_SETTINGS_MODULE=owswims.settings \
 --reload-extra-file=/code/owswims/wsgi.py \
 owswims.asgi:application
