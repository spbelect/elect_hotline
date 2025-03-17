from django.apps import apps, AppConfig

from . import checks


class UfoConfig(AppConfig):
    name = 'ufo'
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        # from .models import Answer
        from . import signals
