from .common import *
from celery.schedules import crontab

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
    #'update-database': {
    #    'task': 'scrapper.scrapper_utils.updateMovieSessions',
    #    'schedule': timedelta(minutes=2),
    #},
    'update-availability': {
        'task': 'scrapper.scrapper_utils.updateSessionsAvailability',
        'schedule': crontab(hour=18, minute=9, day_of_week='wed'),
    }
}