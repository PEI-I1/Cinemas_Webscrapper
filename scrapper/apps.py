from django.apps import AppConfig
import sys, os

class ScrapperConfig(AppConfig):
    name = 'scrapper'

    def ready(self):
        if ("manage.py" in sys.argv or "./manage.py" in sys.argv) and \
          "runserver" in sys.argv:
            if os.getenv('INITIAL_UPDATE', 'true') == 'true':
                from .scrapper_utils import updateDatabaseStartup
                updateDatabaseStartup()
