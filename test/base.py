# -*- coding: utf-8 -*-

import multiprocessing
import time

from collections.abc import Callable
from contextlib import suppress
from os.path import basename, join
from contextlib import contextmanager
from functools import wraps
# from hashlib import md5
# from random import randint
#from tempfile import NamedTemporaryFile
from unittest.mock import patch, Mock
from urllib.parse import parse_qs
from zoneinfo import ZoneInfo

import httpx
import pytest
import responses
import uvicorn

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.db import transaction
from django.test import SimpleTestCase, Client, TestCase
from django.test.client import RequestFactory
from django.utils import translation
from django.utils.decorators import method_decorator

from model_bakery.baker import make
from rest_framework.test import APITestCase

#from utils.shell import compress
#from utils.path import makedirs
from ufo.models import Country, Region


MSK = ZoneInfo('Europe/Moscow')


@pytest.fixture()
def ru():
    return make(Country, id='ru', name='Россия')

@pytest.fixture()
def spb(ru):
    return make(Region, id='ru_78', name='Санкт-Петербург', country=ru, utc_offset=3)

@pytest.fixture()
def msk(ru):
    return make(Region, id='ru_11', name='Москва', country=ru, utc_offset=3)


@pytest.fixture
def uvicorn_server():
    """
    Uvicorn server fixture can be used instead of live_server.
    As it uses asgi, it allows to test sse streaming.
    """
    port = 27901
    multiprocessing.set_start_method('spawn')

    proc = multiprocessing.Process(
        target=uvicorn.run,
        args=('asgi:application',),
        kwargs={'port': port},
        daemon=True
    )
    proc.start()

    # Wait for HTTP 200 response
    while True:
        with suppress(httpx.ConnectError):
            response = httpx.get(f"http://127.0.0.1:{port}")
            if response.status_code is 200:
                print('Uvicorn: connected successfully')
                break
        time.sleep(0.2)

    yield f"http://127.0.0.1:{port}"

    proc.terminate()
    proc.join()  # blocks until the process terminates


@contextmanager
def patch_auth() -> None:
    """
    Patch ska signed url validation to always succeed.

    Usage:
        with patch_auth():
            # Always succeeds to login user
            page.goto(f'{live_server}/auth/login/?auth_user=test@example.com')
    """
    with patch(
            'ska.contrib.django.ska.decorators.validate_signed_request_data',
            lambda *a, **kw: Mock(result=True)):
        yield None


class login():
    """
    Decorator. Decorated playwright test function with `page` argument gets the page
    handler session to have valid login credentials for a user with given email.

    Usage:
        @login('test@example.com')
        def my_user_test(page, live_server):
            pass
    """

    def __init__(self, email):
        """ Initalize decorator instance """
        self.email = email

    def __call__(self, func: Callable) -> Callable:
        """ Returns decorated function that logs in with playwright before execution. """
        @wraps(func)
        def decorated(live_server, page, *a, **kw):
            with patch_auth():
                page.goto(f'{live_server}/auth/login/?auth_user={self.email}')
                return func(live_server, page, *a, **kw)
        return decorated


# NOTE: Not used
class DRFTestCase(APITestCase):
    def _pre_setup(self):
        """
        Mock requests and redis.
        """
        super()._pre_setup()

        responses.start()
        #patch('websubsub.lock.redis', mock_strict_redis_client()).start()
        Country.objects.get_or_create(id='ru')

    def _post_teardown(self):
        """
        Disable all mocks after the test.
        """
        super()._post_teardown()

        responses.reset()
        responses.stop()
        patch.stopall()



class OptimizedTestCase(SimpleTestCase):
    """
    This testcase will not reset database between tests, so database setup may be done once in setUpClass method.
    Database will be reset only in tearDownClass (with transaction rollback).
    As with django TestCase - transactions does not work within the test itself, they are monekeypatched
    to do nothing.
    """

    @classmethod
    def setUpClass(cls):
        super(OptimizedTestCase, cls).setUpClass()
        transaction.enter_transaction_management(using='default')
        transaction.managed(True, using='default')
        cls.client = Client()

        # Flush mail outbox after previous testcases.
        mail.outbox = []

    @classmethod
    def tearDownClass(cls):
        super(OptimizedTestCase, cls).tearDownClass()
        transaction.rollback(using='default')
        transaction.leave_transaction_management(using='default')

