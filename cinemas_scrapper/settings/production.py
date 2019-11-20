from .common import *
from celery.schedules import crontab

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0"
]

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
        'task': 'scrapper.scrapper_utils.updateMovieSessions',
        'schedule': crontab(hour=5, minute=0, day_of_week='thu'),
    }
}