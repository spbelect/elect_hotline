# -*- coding: utf-8 -*-
import re

from datetime import datetime, date, timedelta
from time import sleep
from urllib.parse import parse_qs, urlparse

import django.contrib.auth
import django.test
import jwt
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


@pytest.mark.django_db
@respx.mock(assert_all_mocked=True, assert_all_called=True)
def google_login_success__test(client: django.test.Client, ru, respx_mock):
    """ User should succesfully login with google """

    # WHEN user clicks "Sign in with google"
    response = client.get('/auth/google/start')

    # THEN response status is 302 HttpResponseRedirect
    assert response.status_code == 302

    # AND secret number get stored in request session
    assert 'google_oauth2_state_secret' in client.session

    # AND response redirects to google auth page
    assert response.url.startswith('https://accounts.google.com/o/oauth2/auth?')

    # AND redirect url query has correct arguments
    assert (
        parse_qs(urlparse(response.url).query)
        ==
        {
            'response_type': ['code'],
            'client_id': ['test_google_oauth_client_id'],

            # Callback url which google will redirect to after user authneticates.
            'redirect_uri': ['http://testserver/auth/google/success'],

            'scope': ['https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid'],

            # state is session['google_oauth2_state_secret']
            'state': [client.session['google_oauth2_state_secret']],

            'access_type': ['offline'],
            'include_granted_scopes': ['true'],
            'prompt': ['select_account']
        }
    )

    # GIVEN google oauth2 token server
    google_server = respx_mock.post("https://oauth2.googleapis.com/token").respond(json={
        'id_token': jwt.encode({"email": "user@example.com"}, "secret", algorithm="HS256"),
    })

    # WHEN google redirects to callback page
    response = client.get('/auth/google/success', dict(
        code='123',
        state=client.session['google_oauth2_state_secret'],
        error=''
    ))

    # THEN response satatus code should be 301 redirect
    assert response.status_code == 302

    # AND it should redirect to /answers/history
    assert response.url == '/answers/history'

    user = django.contrib.auth.get_user(client)

    # AND user is authenticated
    assert user.is_authenticated

    # AND user email is user@example.com
    assert user.email == 'user@example.com'
