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


@checks.register("settings")
def settings_check(app_configs, **kwargs):
    messages = []

    if not settings.TURNSTILE_SITE_KEY:
        messages.append(checks.Warning(
            f'TURNSTILE_SITE_KEY env variable is invalid',
            id="Ufo.settings.TURNSTILE_SITE_KEY.invalid"
        ))
    return messages


@checks.register('settings')
def debug_check(app_configs, **kwargs):
    messages = []

    if settings.DEBUG:
        messages.append(checks.Warning(
            f'settings.DEBUG is True',
            id="Ufo.debug.W001"
        ))

    if 'debug_toolbar.middleware.DebugToolbarMiddleware' in settings.MIDDLEWARE:
        messages.append(checks.Warning(
            f'DEBUG_TOOLBAR is enabled',
            id="Ufo.debug.W002"
        ))

    return messages
