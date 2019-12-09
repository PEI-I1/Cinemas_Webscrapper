#!/bin/bash
./manage.py makemigrations
./manage.py migrate
./manage.py loaddata static/cinemas_fixture.json

if [[ $# -eq 2 ]] && [ $1 = "-s" ] ; then
    HOUR=$(date +"%H")
    HOUR_P1=$(echo "($HOUR+1)%24" | bc)
    WEEKDAY=$(echo $(date +"%u") "-1 % 7" | bc)
    DELTA=$2
else
    HOUR="05"
    WEEKDAY="3"
    HOUR_P1="06"
    DELTA="60"
fi
sed -Ee "s/today.weekday\(\) == [0-9] and \(time >= '[0-9]{2}:00:00' and time < '[0-9]{2}:00:00'\)/today.weekday\(\) == "$WEEKDAY" and \(time >= '"$HOUR":00:00' and time < '"$HOUR_P1":00:00'\)/g" -i'' scrapper/scrapper_utils.py
sed -Ee "s/minutes\=[0-9]+/minutes="$DELTA"/g" -i'' cinemas_scrapper/settings/development.py
redis-server &
celery -A cinemas_scrapper.celery worker -B -l info &
./manage.py runserver 0.0.0.0:8000
