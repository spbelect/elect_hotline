# -*- coding: utf-8 -*-
import re

from datetime import datetime, date, timedelta
from collections import OrderedDict

import pendulum
import pytest

from django.conf import settings
from django.core import mail
from django.urls import reverse
from django.test import TestCase
from django.test import override_settings
from django.utils.timezone import localtime, now
from freezegun import freeze_time
from model_bakery.baker import make
from playwright.sync_api import Playwright, Page, expect
from unittest.mock import Mock, patch, ANY

from ufo.models.base import int16
from ufo.models import (
    Region, Country, WebsiteUser, Election, Campaign, Organization, Contact, OrgBranch,
    WebsiteUser, QuizTopic, Question, Answer, MobileUser
)
from ..base import BaseTestCase, patch_auth, MSK, ru, spb, msk



@pytest.mark.uitest
@freeze_time('2024-09-11T00:00:00.000000+03:00')
def create_organization_scenario__test(spb, msk, live_server, page):
    # GIVEN current user is logged in as test@example.com
    with patch_auth():
        page.goto(f'{live_server}/auth/login/signed?auth_user=test@example.com')

    # AND spb_org organization
    spb_org = make(Organization,
        name='SPB organization',
        regions=[spb],
    )
    # # AND actual federal Election
    # president_elections = make(Election,
    #     id='election-id-fed-actual',
    #     name='Выборы президента',
    #     date = date.today() + timedelta(days=10),
    # )

    ######
    # WHEN user opens organizations page
    page.goto(f"{live_server}/organizations")

    # THEN SPB organization should be displayed in the list
    expect(page.get_by_role("heading", name="SPB organization")).to_be_visible()

    # AND create organization button should be visible
    expect(page.get_by_role("link", name="Create")).to_be_visible()

    # WHEN user selects filter by region MSK
    page.get_by_label("Filter by region").click()
    page.get_by_label("Filter by region").select_option("ru_11")

    # THEN SPB organization should be hidden
    expect(page.get_by_role("heading", name="SPB organization")).to_have_count(0)


    # WHEN user clicks create button
    page.get_by_role("link", name="Create").click()

    ######
    # THEN organization edit form page opens
    # AND name input should be visible
    expect(page.get_by_placeholder("Name")).to_be_visible()

    # WHEN user fills name
    page.get_by_placeholder("Name").fill("My MSK Org")

    # AND click regions
    page.get_by_placeholder("Regions").click()

    # AND selects "Москва"
    page.get_by_role("option", name="Москва").click()


    page.get_by_role("button", name="Create").click()

    #########
    # THEN organizations list page opens
    # AND success message should be visible
    expect(page.get_by_text("Organization My MSK Org successfully created.")).to_be_visible()

    # AND My MSK org should be displayed in the list
    expect(page.get_by_role("heading", name="My MSK org")).to_be_visible()

    # AND SPB organization should be displayed in the list
    expect(page.get_by_role("heading", name="SPB organization")).to_be_visible()

    # WHEN user selects filter by region MSK
    page.get_by_label("Filter by region").click()
    page.get_by_label("Filter by region").select_option("ru_11")

    # THEN SPB organization should be hidden
    expect(page.get_by_role("heading", name="SPB organization")).to_have_count(0)

    # AND My MSK org should stil be displayed in the list
    expect(page.get_by_role("heading", name="My MSK org")).to_be_visible()
