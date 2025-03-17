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
def google_login_invalid_token__test(client: django.test.Client, ru, respx_mock):
    """
    User should see error messages if google oauth server responds with invalid jwt token.
    """

    # WHEN user clicks "Sign in with google"
    response = client.get('/auth/google/start')

    # THEN response status is 302 HttpResponseRedirect
    assert response.status_code == 302

    # AND secret number get stored in request session
    assert 'google_oauth2_state_secret' in client.session

    # GIVEN google oauth2 token server which returns invalid jwt token
    google_server = respx_mock.post("https://oauth2.googleapis.com/token").respond(json={
        'id_token': "THIS IS NOT JSON AT ALL",
    })

    # WHEN google redirects to callback page with correct parameters
    response = client.get('/auth/google/success', dict(
        code='123',
        state=client.session['google_oauth2_state_secret'],
        error=''
    ))

    # THEN response satatus code should be 401 Unauthorized
    assert response.status_code == 401

    # AND response content should contain error message
    assert "Authentication failed" in str(response.content)

    # AND user is not authenticated
    assert django.contrib.auth.get_user(client).is_authenticated is False

