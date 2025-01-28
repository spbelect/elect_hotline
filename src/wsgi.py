"""
WSGI config for project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import logging
import multiprocessing
import os
import sys
import traceback
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from django.conf import settings

# import utils.mail

sys.path.insert(0, str(Path(__file__).parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

#try:
    #application = get_wsgi_application()
#except Exception as e:
    ## Recipe from http://stackoverflow.com/questions/30954398/django-populate-isnt-reentrant
    ## Should print actual traceback on "RuntimeError: populate() isn't reentrant"
    #print(f'handling WSGI exception {e}')
    #if 'mod_wsgi' in sys.modules:
        #import signal
        #import time
        #traceback.print_exc()
        #os.kill(os.getpid(), signal.SIGINT)
        #time.sleep(2.5)

application = get_wsgi_application()
app = application

### NOTE: You have to use gunicorn `--preload` option to share the lock
### between all workers
### Only first worker will succeesfully acquire the lock.
# lock = multiprocessing.Lock()
# is_first_worker = lock.acquire(False)


#try:
    #if is_first_worker:
        #if settings.DEBUG:
            #logger.warning("DEBUG is True! Do not use this in production!")

        ## Check email server connection settings.
        #logger.info("Checking email connection...")
        #utils.mail.check_smtp_settings()

        ## Send startup email.
        #if getattr(settings, 'WSGI_EMAIL_SEND_ON_START', False):
            #if 'mod_wsgi' in sys.modules or 'gunicorn' in sys.modules:
                #logger.info("Sending startup email...\n"
                            #"Set settings.WSGI_EMAIL_SEND_ON_START to False to disable")
                #utils.mail.mail_admins(
                    #subject='Server started',
                    #message='wsgi.py: server started.\n' \
                        #'Set settings.WSGI_EMAIL_SEND_ON_START to False to disable notification',
                    #backend='django.core.mail.backends.smtp.EmailBackend')
            #else:
                #logger.info("Ignoring WSGI_EMAIL_SEND_ON_START, as no"
                            #" mod_wsgi or gunicorn found in sys.modules.")

#except Exception as e:
    #import traceback
    #traceback.print_exc()
    #logger.exception(str(e))
    #raise

logger = logging.getLogger('wsgi.py')
logger.info("App started.")
