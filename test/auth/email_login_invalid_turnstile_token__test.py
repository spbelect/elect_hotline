# -*- coding: utf-8 -*-
import re

from datetime import datetime, date, timedelta
from time import sleep
from urllib.parse import parse_qs, urlparse

import django.contrib.auth
import django.test
import pendulum
import pytest
import respx
import time_machine

from django.conf import settings
from django.core import mail
from django.db import transaction
from django.urls import reverse
from django.test import TestCase
from django.test import override_settings
from django.utils.timezone import localtime, now
from loguru import logger
from model_bakery.baker import make
from playwright.sync_api import Playwright, Page, expect
from unittest.mock import Mock, patch, ANY

from ufo.models.base import int16
from ufo.models import (
    Region, Country, WebsiteUser, Election, Campaign, Organization, Contact, OrgBranch,
    WebsiteUser, QuizTopic, Question, Answer, OrgMembership
)

from .. import base
from ..base import MSK, ru, spb, msk

@respx.mock(assert_all_mocked=True)
@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND='anymail.backends.test.EmailBackend',
    TURNSTILE_SITE_KEY='123'
)
def email_login_invalid_turstile__test(client: django.test.Client, ru, respx_mock):
    """ User should see an error when turnstile validation fails """

    # GIVEN turnstile server that always returns failure
    turnstile_server = respx_mock.post(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    ).respond(json={'success': False})

    # WHEN user submits email login form
    response = client.post('/auth/login', dict(email='user@example.com', turnstile_token="123"))

    # THEN response status is 422 (Unprocessable Content)
    assert response.status_code == 422

    # AND request is sent to turnstile server
    assert turnstile_server.called

    # AND no email is sent
    assert len(mail.outbox) == 0
