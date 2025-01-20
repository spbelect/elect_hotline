# -*- coding: UTF-8 -*-
from __future__ import absolute_import

import logging
import smtplib

from django.conf import settings
from django.core.mail import EmailMessage


class ImproperlyConfigured(Exception):
    pass


class BufferingSMTPHandler(logging.handlers.BufferingHandler):
    def __init__(self, mailhost, fromaddr, toaddrs, subject, credentials, capacity):
        logging.handlers.BufferingHandler.__init__(self, capacity)

            #'mailhost': (EMAIL_HOST, EMAIL_PORT),
            #'fromaddr': EMAIL_HOST_USER,
            #'toaddrs': 'someuniquename@gmail.com',
            #'subject': 'gotender log',
            #'credentials': (EMAIL_HOST_USER, EMAIL_HOST_PASSWORD),
            #'secure': tuple(),

        self.mailhost = mailhost
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        self.subject = subject
        self.setFormatter(logging.Formatter("%(asctime)s %(levelname)-5s %(message)s"))

    def flush(self):
        if len(self.buffer) == 0:
            return

        try:
            if isinstance(self.mailhost, tuple):
                host, port = self.mailhost
            else:
                host = self.mailhost
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(host, port)
            msg = "\r\n".join(map(self.format, self.buffer))
            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()
        except:
            self.handleError(None)  # no particular record
        self.buffer = []


class DjangoBufferingSMTPHandler(logging.handlers.BufferingHandler):
    def __init__(self, capacity, toaddrs=None, subject=None):
        logging.handlers.BufferingHandler.__init__(self, capacity)

        if toaddrs:
            self.toaddrs = toaddrs
        else:
            # Send messages to site administrators by default
            if not settings.ADMINS:
                raise ImproperlyConfigured('DjangoBufferingSMTPHandler requires toaddrs kwarg or settings.ADMINS to be provided.')
            self.toaddrs = zip(*settings.ADMINS)[-1]

        if subject:
            self.subject = subject
        else:
            self.subject = 'logging'

    def flush(self):
        if len(self.buffer) == 0:
            return

        try:
            msg = "\r\n".join(map(self.format, self.buffer))
            emsg = EmailMessage(self.subject, msg, to=self.toaddrs)
            emsg.send()
        except Exception:
            # handleError() will print exception info to stderr if logging.raiseExceptions is True
            self.handleError(record=None)
        self.buffer = []
