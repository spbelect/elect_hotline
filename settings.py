#import logging
import os
import re
import sys
import traceback
from os.path import abspath, basename, dirname, join, exists

import jinja2
import environ

from django.utils.translation import gettext_lazy as _


print(f'{os.environ["DJANGO_SETTINGS_MODULE"]=}')

env = environ.Env()

SRC_DIR = environ.Path(__file__) - 1  # ./

env.read_env(SRC_DIR('env-local'))

# Support for DATABASE_URL=sqlite:///{SRC_DIR}/db.sqlite
os.environ['DATABASE_URL'] = env('DATABASE_URL').format(SRC_DIR=SRC_DIR)

DEBUG = env.bool('DJANGO_DEBUG', default=False)

DOMAIN_NAME = env('DOMAIN_NAME', default='127.0.0.1:8000')

ALLOWED_HOSTS = ['*'] if DEBUG else ['127.0.0.1', DOMAIN_NAME]


SECRET_KEY = env('DJANGO_SECRET_KEY')

SKA_SECRET_KEY = env('SKA_SECRET_KEY', default=SECRET_KEY)
SKA_UNAUTHORISED_REQUEST_ERROR_TEMPLATE = '401_email_link_invalid.html'


ADMINS = MANAGERS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    # This app is not needed.
    # "whitenoise.runserver_nostatic",

    # NOTE: Default django staticfiles app should be disabled in tests due to
    # conflict with whitenoise in pytest-django live_server.
    'django.contrib.staticfiles',

    'django.contrib.humanize',

    'adminsortable2',
    'django_extensions',
    'django_select2',
    'django_jsonform',
    # 'django_jinja',
    # 'webpack_loader',
    'prettyjson',
    'rest_framework',
    
    'ufo.apps.UfoConfig',
]


if 'SENTRY_DSN' in os.environ:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=env('SENTRY_DSN'),
        integrations=[DjangoIntegration()]
    )



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # The WhiteNoise middleware should be placed directly after the
    # Django SecurityMiddleware and before all other middleware.
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # Annotate AnonymousUser with persistent properties which are stored
    # in the session.
    'ufo.middleware.anonymous_user_session',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        #'BACKEND': "django_jinja.backend.Jinja2",
        'DIRS': ['ufo/', SRC_DIR('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'line_statement_prefix': '# ',
            'line_comment_prefix': '##',
            #"match_extension": ".html",
            'undefined': jinja2.ChainableUndefined,

            # Environment has global context variables independent of request.
            'environment': 'ufo.views.context.jinja_env',
            'extensions': [
                'jinja2.ext.i18n',
                'ufo.jinja_extensions.LanguageExtension',
                #'jdj_tags.extensions.DjangoStatic',
                # 'jdj_tags.extensions.DjangoI18n',
                # 'jdj_tags.extensions.DjangoL10n',
            ],
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Sets context variables depending on request.
                'ufo.views.context.context_processor'
            ],
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [SRC_DIR('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]


# ./manage.py runserver will use WSGI_APPLICATION
WSGI_APPLICATION = 'wsgi.application'

AUTH_PASSWORD_VALIDATORS = []

LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
]

LANGUAGE_CODE = 'en-us'
# LANGUAGE_CODE = 'ru'

LOCALE_PATHS = [SRC_DIR('locale')]

# # No idea why python requires this
# import locale
# try:
#     locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
# except Exception as e:
#     print(f"Can't set locale.LC_ALL='en_US.UTF8':\n{e}")

TIME_ZONE = 'UTC'
#TIME_ZONE = 'Europe/Moscow'

USE_I18N = True
USE_TZ = True


DATABASES = {'default': env.db('DATABASE_URL', default='')}
DATABASES['default']['ATOMIC_REQUESTS'] = True
DATABASES['default']['CONN_MAX_AGE'] = 0

if DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
    DATABASES['default']['OPTIONS'] = {
        # Transaction mode IMMEDIATE resolves
        # django.db.utils.OperationalError: database is locked
        "transaction_mode": "IMMEDIATE",

        "timeout": 6000,
        "init_command": ' '.join([
            # https://www.sqlite.org/pragma.html#pragma_synchronous
            #
            #  EXTRA (3): like FULL with the addition that the directory containing a rollback
            # journal is synced after that journal is unlinked to commit a transaction in
            # DELETE mode.
            #  FULL (2): database engine will use the xSync method of the VFS to ensure
            # that all content is safely written to the disk surface prior to continuing.
            #  NORMAL (1): database engine will still sync at the most critical moments, but
            # less often than in FULL mode.
            #  OFF (0): SQLite continues without syncing as soon as it has handed data off to
            # the operating system.
            # "PRAGMA synchronous=EXTRA;",
            # "PRAGMA synchronous=NORMAL;",
            # "PRAGMA synchronous=OFF;",
            # "PRAGMA cache_size=2000;"
            "PRAGMA journal_mode=WAL;"
        ]),
    }


STATICFILES_DIRS = [SRC_DIR('static/'),]
STATIC_ROOT = SRC_DIR('static_collected/')
STATIC_URL = '/static/'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

### Страницы логина у нас нет. Сюда будет редирект от декратора @login_required
LOGIN_URL = '/feed/answers/'


import logging
import loguru
import logging_to_loguru

# Redirect all stdlib logging to loguru
logging.basicConfig(handlers=[logging_to_loguru.ToLoguru()], level=0, force=True)


LOGGING_CONFIG = None  # Prevent django standard logging setup


# Loguru settings
loguru.logger.configure(handlers=[
    dict(
        sink = sys.stderr,
        # format="[{time}] {message}",
        level = "DEBUG",
        colorize = True,
        backtrace = True,
        diagnose = True,
        filter = {
            "": os.environ.get("UFO_LOGLEVEL", "INFO"),

            "django": os.environ.get("UFO_LOGLEVEL", "INFO"),
            "django.db": "INFO",
            "django.db.backends.base.schema": "INFO",
            "django.utils.autoreload": "ERROR",

            "environ.environ": "INFO",

            "ufo": os.environ.get("UFO_LOGLEVEL", "INFO"),
        }
    ),
    # dict(sink="file.log", enqueue=True, serialize=True),
])


#WEBPACK_LOADER = {
    #'DEFAULT': {
        #'BUNDLE_DIR_NAME': 'bundles/',
        #'STATS_FILE': SRC_DIR('webpack-stats.json'),
    #}
#}

AUTH_USER_MODEL = 'ufo.WebsiteUser'


EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_PORT = env.int('EMAIL_PORT', default='25')
EMAIL_HOST = env.str('EMAIL_HOST', default='smtp.yandex.ru')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='example@yandex.ru')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')

### The 'SERVER_EMAIL' is used by django.core.mail.mail_admins() as source address.
SERVER_EMAIL = env.str('SERVER_EMAIL', default=EMAIL_HOST_USER)

### The 'DEFAULT_FROM_EMAIL' is used everywhere else as default source address.
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)


#EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
EMAIL_BACKEND = env.str('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

#EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
ANYMAIL = {
    "SENDGRID_API_KEY": env.str('SENDGRID_API_KEY', default=None),
}

ADMIN_EMAIL = env.str('ADMIN_EMAIL')
FAKE_TIK_EMAILS = env.bool('FAKE_TIK_EMAILS', default=True)
TIK_EMAIL_MODERATION = env.bool('TIK_EMAIL_MODERATION', default=True)

### The 'EMAIL_SUBJECT_PREFIX' is used by django.core.mail.mail_admins()
### and django.core.mail.mail_managers()
### Guess server urls from 'ALLOWED_HOSTS'
server_urls = ' / '.join(x for x in ALLOWED_HOSTS if x not in ['127.0.0.1', '*'])
if server_urls:
    EMAIL_SUBJECT_PREFIX = server_urls + ' '


SUBMIT_GOOGLE_PROTO = env.bool('SUBMIT_GOOGLE_PROTO', default=False)

AWS_SECRET_KEY = env('DJANGO_AWS_SECRET_KEY', default='')
AWS_ACCESS_KEY = env('DJANGO_AWS_ACCESS_KEY', default='')


from loguru import logger
import pydantic


def drf_exc_handler(exc: Exception, context):
    """ Rest framework exception handler. """
    from rest_framework.views import exception_handler
    from rest_framework.response import Response
    
    if isinstance(exc, pydantic.ValidationError):
        logger.warning(str(exc))
        return Response(status=400, data={
            'status': 'validation error', 
            'errors': [f'{x["loc"][0]}: {x["msg"]}' for x in exc.errors()]
        })
    
    if DEBUG:
        return None   # raise validation exceptions.
    
    return exception_handler(exc, context)


REST_FRAMEWORK = {
    #'EXCEPTION_HANDLER': lambda *a: None,  # raise validation exceptions.
    'EXCEPTION_HANDLER': drf_exc_handler
}

GOOGLE_OAUTH2_CLIENT_ID = env.str('GOOGLE_OAUTH2_CLIENT_ID')
GOOGLE_OAUTH2_CLIENT_SECRET = env.str('GOOGLE_OAUTH2_CLIENT_SECRET')

INTERNAL_IPS = [
    # debug toolbar is shown only for internal ip
    # unless SHOW_TOOLBAR_CALLBACK is overriden
    "127.0.0.1",
]

if env.bool('DEBUG_TOOLBAR', default=False):
    print('DEBUG_TOOLBAR is enabled')

    DEBUG_TOOLBAR_CONFIG = {
        #'SHOW_TOOLBAR_CALLBACK': lambda request: False,
        # 'SHOW_TOOLBAR_CALLBACK': lambda request: True,
        #'SHOW_TOOLBAR_CALLBACK': lambda request: request.user.is_authenticated(),
        # 'SHOW_TOOLBAR_CALLBACK': lambda request: request.user.is_superuser,
        'INTERCEPT_REDIRECTS': False,
    }

    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        #'debug_toolbar.panels.settings_vars.SettingsVarsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        #'debug_toolbar.panels.logger.LoggingPanel',
        'debug_toolbar.panels.cache.CachePanel'
        #'debug_profiling.ProfilingPanel',
    )

    DEBUG_TOOLBAR_PATCH_SETTINGS = False

    if 'test' not in sys.argv:
        INSTALLED_APPS += ['debug_toolbar',]
        MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
        DEBUG_TOOLBAR_PATCH_SETTINGS = True
else:
    print('DEBUG_TOOLBAR is disabled')
