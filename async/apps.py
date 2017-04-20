from django.apps import AppConfig


class AsyncConfig(AppConfig):
    name = 'async'

    def ready(self):
        self.module.autodiscover()
