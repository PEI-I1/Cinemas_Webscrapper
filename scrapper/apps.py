from django.apps import AppConfig

class ScrapperConfig(AppConfig):
    name = 'scrapper'

    def ready(self):
        from .scrapper_utils import updateDatabaseStartup
        updateDatabaseStartup()
