from .common import *
from datetime import timedelta
#from celery.schedules import crontab

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Celery update database task

CELERY_BEAT_SCHEDULE = {
    'update-database': {
        'task': 'scrapper.scrapper_utils.updateDatabase',
        'schedule': timedelta(minutes=60),
        #'schedule': crontab(hour=12, minute=54, day_of_week=1)
    },
}

