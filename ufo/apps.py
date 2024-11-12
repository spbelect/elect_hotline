# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.conf import settings
from django.core import checks
from django.core.mail import EmailMessage


@checks.register("email", deploy=True)
def my_check(app_configs, **kwargs):
    messages = []

    email = EmailMessage(
        subject = 'Test email from ufo',
        body = 'Hello world',
        from_email = f'"Election Hotline" <{settings.DEFAULT_FROM_EMAIL}>',
        to = [settings.ADMIN_EMAIL]
    )
    print(f'Sending email to {settings.ADMIN_EMAIL}')
    try:
        email.send()
    except Exception as err:
        messages.append(checks.Warning(
            f'Sending test email failed with {err!r}',
            id="Ufo.email.W001"
        ))
    return messages


class UfoConfig(AppConfig):
    name = 'ufo'
    default_auto_field = 'django.db.models.AutoField'

    #def ready(self):
        #from .models import Answer
        
