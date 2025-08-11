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
def email_login_success__test(client: django.test.Client, ru, respx_mock):
    """ User should succesfully login with email """

    # GIVEN turnstile server that always returns success
    turnstile_server = respx_mock.post(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    ).respond(json={'success': True})

    # WHEN user submits email login form
    response = client.post('/auth/login', dict(email='user@example.com', turnstile_token="123"))

    # THEN response status is 200 (Success)
    assert response.status_code == 200

    # AND 1 email is sent
    assert len(mail.outbox) == 1
    # to user
    assert mail.outbox[0].to == ['user@example.com']
    # AND has a link to sign-in
    assert mail.outbox[0].body.startswith('Link to sign in: ')

    link = mail.outbox[0].body.split('Link to sign in: ')[-1]

    # WHEN user opens the received link
    response = client.get(link)

    # THEN response satatus code should be 301 redirect
    assert response.status_code == 302

    # AND it should redirect to /
    assert response.url == '/'

    user = django.contrib.auth.get_user(client)

    # AND user is authenticated
    assert user.is_authenticated

    # AND user email is user@example.com
    assert user.email == 'user@example.com'

    # AND django_emails_sent_total prometheus counter is updated
    metrics = dict(x.split()
        for x in client.get('/metrics').content.decode().split('\n')
        if x and not x.startswith('#')
    )

    assert metrics['django_emails_sent_total{destination="user@example.com"}'] == '1.0'
    assert 'django_emails_sent_created{destination="user@example.com"}' in metrics


    # from prometheus_client.parser import text_string_to_metric_families
    # response = client.get('/metrics').content.decode()
    # metrics{x.name: x for x in text_string_to_metric_families(response)}

    # assert metrics['django_emails_sent'].samples[0].value == 1.0

