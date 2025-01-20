# -*- coding: UTF-8 -*-
from __future__ import absolute_import

import socket

from django.core import mail
from django.conf import settings


def mail_admins(subject, message, from_email=None, backend=None, **kwargs):
    """
    This is more advanced version of django.core.mail.mail_admins(). It works the same, but additionally
    allows to specify `backend` and `from_email`.
    By default `from_email` will be settings.SERVER_EMAIL, as in django.core.mail.mail_admins()
    """
    connection = None
    if backend:
        connection = mail.get_connection(backend=backend)

    if not from_email:
        from_email = settings.SERVER_EMAIL

    admins = list(zip(*settings.ADMINS))[-1]
    subject = '%s%s' % (settings.EMAIL_SUBJECT_PREFIX, subject)

    mail.send_mail(subject, message, from_email, recipient_list=admins, connection=connection, **kwargs)


class socket_default_timeout(object):
    """
    This decorator will override socket default timeout, and restore previous value before exit.
    Decorator has one required argumant - `timeout`.

    Usage:

    @socket_default_timeout(5)
    def my_function():
        pass

    """
    def __init__(self, timeout):
        self.timeout = timeout

    def __call__(self, f):
        def wrapped(*args, **kwargs):
            default_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(self.timeout)
            try:
                return f(*args, **kwargs)
            finally:
                socket.setdefaulttimeout(default_timeout)

        return wrapped


@socket_default_timeout(5)
def check_smtp_settings():
    connection = mail.get_connection(backend='django.core.mail.backends.smtp.EmailBackend')
    try:
        connection.open()
    except socket.timeout:
        message = 'EMAIL_HOST "%s" does not respond.' % settings.EMAIL_HOST
        raise Exception(message)
    except socket.error:
        message = 'Can\'t connect to EMAIL_PORT %s of "%s" host.' % (settings.EMAIL_PORT, settings.EMAIL_HOST)
        raise Exception(message)
    # except smtplib.SMTPAuthenticationError:

    finally:
        connection.close()
