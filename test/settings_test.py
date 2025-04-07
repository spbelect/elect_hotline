import environ

env = environ.Env()

SRC_DIR = environ.Path(__file__) - 1  # src/
env.read_env(SRC_DIR('env-localtest'))  # overrides env-local

from settings import *

# Simple guard that we are using test database
assert 'test' in DATABASES['default']["NAME"]

DATABASES['default'].update({
    "TEST": {
        # Set the test database name explicitly. Otherwise django will
        # prepend "test_" to the name. Some tests use external live uvicorn
        # server which will fail to connect to the database, because it
        # uses DATABASES['default']["NAME"] without "test_" prefix.
        "NAME": DATABASES['default']["NAME"]
    },
})

ANSWERS_SSE_ENGINE = 'views.answers.sse.poll_database'

# Speed up sse polling
ANSWERS_SSE_POLL_DB_DELAY = 0.1


RAISE_404 = True

# This setting does nothing. Django test runner overrides email backend
# So we currently change it only on selected tests with
# django.test.override_settings() decorator.
# EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
EMAIL_BACKEND = 'anymail.backends.test.EmailBackend'

#EMAIL_BACKEND = 'eml_email_backend.EmailBackend'
##EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = SRC_DIR('eml_mails')

ADMIN_EMAIL = 'test@example.com'

# Speedup login during tests.
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)


# NOTE: Default django staticfiles app should be disabled in tests due to
# conflict with whitenoise in pytest-django live_server.
INSTALLED_APPS.remove('django.contrib.staticfiles')


REST_FRAMEWORK = {
    ## 'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'EXCEPTION_HANDLER': lambda *a: None,  # raise validation exceptions during tests.
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}


#update(LOGGING, {
    #'loggers': {
        #'django.db.backends': {'level': 'ERROR'},  # Prevent flood when assertNumQueries() called
    #}
#})

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
    #'default': {
        # TODO: check 'lrucache_backend.LRUObjectCache'

        # NOTE: deprecated?
        #'BACKEND': 'test.cache_backend.LocMemNoPickleCache',  # This backend can store Mock.
    #}
}


GOOGLE_OAUTH2_CLIENT_ID = 'test_google_oauth_client_id'
GOOGLE_OAUTH2_CLIENT_SECRET = 'test_google_oauth_client_secret'
