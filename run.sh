#!/bin/bash
./manage.py makemigrations
./manage.py migrate
./manage.py loaddata static/cinemas_fixture.json

redis-server &
celery -A cinemas_scrapper.celery worker -B -l info &
./manage.py runserver
