import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinemas_scrapper.settings.development')

app = Celery("cinemas_scrapper")

# All celery configuration variables have a 'CELERY_' prefix
app.config_from_object("django.conf:settings", namespace='CELERY')
app.autodiscover_tasks()
