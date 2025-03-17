# -*- coding: utf-8 -*-
from django.apps import apps, AppConfig
from django.conf import settings
from django.core import checks
from django.core.mail import EmailMessage


@checks.register("email", deploy=True)
def email_check(app_configs, **kwargs):
    messages = []

    print(f'Using {settings.EMAIL_BACKEND=}')

    if settings.EMAIL_BACKEND == 'anymail.backends.sendgrid.EmailBackend':
        if not settings.__dict__.get('SENDGRID_API_KEY'):
            messages.append(checks.Warning(
                f'settings.EMAIL_BACKEND is anymail, but settings.SENDGRID_API_KEY is not set',
                id="Ufo.email.W002"
            ))

            return messages

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

    def ready(self):
        # from .models import Answer
        from . import signals
