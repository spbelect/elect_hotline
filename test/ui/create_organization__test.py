# -*- coding: utf-8 -*-
import re

from datetime import datetime, date, timedelta
from collections import OrderedDict

import pendulum
import pytest

from django.conf import settings
from django.core import mail
from django.db import transaction
from django.urls import reverse
from django.test import TestCase
from django.test import override_settings
from django.utils.timezone import localtime, now
from freezegun import freeze_time
from loguru import logger
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
def create_organization_scenario__test(live_server, spb, msk, page):

    # GIVEN existing SPB organization
    spb_org = make(Organization,
        name='SPB organization',
        regions=[spb],
        creator__email='somone_else@ex.com'
    )
    page.wait_for_timeout(500)  # Wait for sqlite database requests to finish

    # AND current user is logged in as test@example.com
    with patch_auth():
        page.goto(f'{live_server}/auth/login/signed?auth_user=test@example.com')

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


    ######

    # WHEN user clicks create button
    page.get_by_role("link", name="Create").click()

    # THEN new organization edit form page opens
    # AND name input should be visible
    expect(page.get_by_placeholder("Name")).to_be_visible()

    page.wait_for_timeout(1000)  # Wait alpine-js init

    # WHEN user fills name
    page.get_by_placeholder("Name").fill("My MSK Org")

    # AND press enter
    page.keyboard.press('Enter')

    # THEN
    expect(page.get_by_label("regions validation error")).to_be_visible()

    # AND click regions
    page.get_by_placeholder("Regions").click()

    # AND selects "Москва"
    page.get_by_role("option", name="Москва").click()

    # THEN
    expect(page.get_by_label("regions validation error")).to_have_count(0)

    # AND uik ranges for Moskva should be visible
    expect(page.get_by_text("Москва UIK ranges All")).to_be_visible()

    # page.wait_for_timeout(500)  # Wait for sqlite database requests to finish

    # AND database should contain 2 orgs: old and newly created org
    assert set(Organization.objects.values_list('name', 'creator__email')) == {
        ('SPB organization', 'somone_else@ex.com'),
        ('My MSK Org', 'test@example.com')
    }

    # page.wait_for_timeout(500)  # Wait for sqlite database requests to finish

    #########

    # WHEN user clicks uik ranges
    page.get_by_text("Москва UIK ranges All").get_by_role("link", name="UIK ranges All").click()

    # THEN UIK Ranges page opens
    # AND UIK Ranges page header should be visible
    expect(page.get_by_role("heading", name="UIK Ranges Москва")).to_be_visible()

    # AND first empty UIK range input should be visible
    expect(page.get_by_placeholder("From").nth(0)).to_be_visible()

    # AND Save button should be disabled
    expect(page.get_by_text("Save")).to_be_disabled()

    # WHEN user fills first range "from" and "to" inputs
    page.get_by_placeholder("From").nth(0).fill('1')
    page.get_by_placeholder("To").nth(0).fill('10')

    # THEN Save button should become enabled
    expect(page.get_by_text("Save")).to_be_enabled()

    # WHEN user clicks "more"
    page.get_by_label("Add range").click()

    # TEHN second empty UIK range input should become visible
    expect(page.get_by_placeholder("From").nth(1)).to_be_visible()

    # AND Save button should become disabled again
    expect(page.get_by_text("Save")).to_be_disabled()

    # WHEN user fills second range "from" and "to" inputs
    page.get_by_placeholder("From").nth(1).fill('15')
    page.get_by_placeholder("To").nth(1).fill('20')

    # THEN Save button should become enabled
    expect(page.get_by_text("Save")).to_be_enabled()

    # WHEN user clicks "Save"
    page.get_by_text("Save").click()

    # THEN edit organization page opens
    # AND Moskva region should have saved UIK ranges
    expect(page.get_by_text("Москва UIK ranges 1-10 15-20")).to_be_visible()

    #########

    # WHEN user clicks topleft menu drawer
    page.get_by_role("navigation").get_by_role("button").click()

    # AND clicks organizations link
    page.get_by_role("link", name="Organizations").click()

    # THEN organizations list page opens
    # AND list count should display 2 found organizations
    expect(page.get_by_text("Found 2 organizations")).to_be_visible()

    # AND Create new organization button should be hidden
    expect(page.get_by_role("link", name="Create")).to_have_count(0)

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
