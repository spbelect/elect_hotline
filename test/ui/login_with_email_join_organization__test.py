# -*- coding: utf-8 -*-
import re

from datetime import datetime, date, timedelta

import pendulum
import pytest
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


@pytest.mark.uitest
@time_machine.travel(datetime(2024, 9, 16, tzinfo=MSK), tick=False)
def login_with_email_join_organization_scenario__test(live_server, spb, msk, page):
    """ User logs in, and becomes member via organization invite """

    # GIVEN existing SPB organization
    spb_org = make(Organization,
        name='SPB organization',
        regions=[spb],
        creator__email='somone_else@ex.com'
    )

    # AND pending invitation for user@example.com
    membership = make(OrgMembership,
        organization=spb_org,
        user__email='user@example.com',
        role='invited'
    )
    page.wait_for_timeout(500)  # Wait for sqlite database requests to finish

    # WHEN user opens login page
    page.goto(f'{live_server}/auth/login')

    # THEN email input should be visible
    expect(page.get_by_placeholder("Enter email address")).to_be_visible()

    # WHEN user fills invalid email
    page.get_by_placeholder("Enter email address").fill('lala')

    # THEN Send button should be disabled
    expect(page.get_by_role("button", name="Send")).to_be_disabled()

    # WHEN user fills another invalid email which ends with number
    page.get_by_placeholder("Enter email address").fill('lala@g.4')

    # THEN Send button should be enabled
    expect(page.get_by_role("button", name="Send")).to_be_enabled()

    # WHEN user clicks "Send"
    page.get_by_role("button", name="Send").click()

    # THEN email validation error should be visible
    expect(page.get_by_label("email validation error")).to_be_visible()

    # WHEN user fills valid email
    page.get_by_placeholder("Enter email address").fill('user@example.com')

    # AND user clicks "Send"
    page.get_by_role("button", name="Send").click()

    # THEN email validation error should be hidden
    expect(page.get_by_label("email validation error")).to_have_count(0)

    # AND Send button should be disabled
    expect(page.get_by_role("button", name="Send")).to_be_disabled()

    # AND email input should be disabled
    expect(page.get_by_placeholder("Enter email address")).to_be_disabled()

    # AND success text should be visible
    expect(page.get_by_text("Login link sent")).to_be_visible()

    # AND 1 email sent
    assert len(mail.outbox) == 1
    # to user
    assert mail.outbox[0].to == ['user@example.com']
    # AND has a link to sign-in
    assert mail.outbox[0].body.startswith('Link to sign in: ')

    link = mail.outbox[0].body.split('Link to sign in: ')[-1]

    # WHEN user opens the link
    page.goto(link)

    # THEN success text should be visible
    expect(page.get_by_text("You have successfully logged in as user@example.com")).to_be_visible()

    # WHEN user clicks navigation menu
    page.get_by_label("Navigation Menu").click()

    # THEN sign out button should be visible
    expect(page.get_by_role("link", name="Sign out")).to_be_visible()

    # AND organization role should change from 'invited' to 'operator'
    assert (
        list(OrgMembership.objects.values('user__email', 'organization_id', 'role'))
        ==
        [
            {
                'user__email': 'somone_else@ex.com',
                'organization_id': str(spb_org.id),
                'role': 'admin',
            },
            {
                'user__email': 'user@example.com',
                'organization_id': str(spb_org.id),
                'role': 'operator',
            }
        ]
    )

    # AND organization creator should receive new member join notification
    assert (
        WebsiteUser.objects.get(id=spb_org.creator_id).unread_notifications
        ==
        [
            'Пользователь user@example.com присоединился к организации SPB organization',
        ]
    )
