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

from .. import base
from ..base import MSK, ru, spb, msk


@pytest.mark.uitest
@freeze_time('2024-09-11T00:00:00.000000+03:00')
def filter_history_new_scenario__test(live_server, spb, msk, page):
    # GIVEN current user is logged in as test@example.com
    with base.patch_auth():
        page.goto(f'{live_server}/auth/login/signed?auth_user=test@example.com')

    page.wait_for_timeout(500)  # Wait for sqlite database requests to finish

    # AND actual federal Election
    president_elections = make(Election,
        id='election-id-fed-actual',
        name='Выборы президента',
        date = date.today() + timedelta(days=10),
    )
    # AND 2 actual regional Elections
    guber_spb = make(Election,
        id='election-id-spb-actual',
        name='Выборы губернатора спб',
        date = date.today() + timedelta(days=10),
        region=spb
    )
    guber_msk = make(Election,
        id='election-id-msk-actual',
        name='Выборы губернатора мск',
        date = date.today() + timedelta(days=10),
        region=msk
    )

    # AND 2 old Elections
    make(Election,
        id='election-id-fed-2013',  name='Федеральные Выборы 2013', date=date(2013, 4, 4),
    )
    old_spb_election = make(Election,
        id='election-id-spb-2013',  name='Cпб Выборы 2013', date=date(2013, 4, 4), region=spb
    )

    org = make(Organization, members=[WebsiteUser.objects.get(email="test@example.com")])
    make(Campaign, organization=org, election=president_elections)
    # AND quiz topic with 2 questions
    topic = make(QuizTopic, name='ДО НАЧАЛА ГОЛОСОВАНИЯ', questions=[
        make(Question, id='vam_predostavili', label='вам предоставили', type='YESNO'),
        make(Question, id='vbros', label='вброс', type='YESNO')
    ])

    # AND Mobile user
    appuser = make(MobileUser,
         id='123', elections=[old_spb_election, guber_spb, president_elections]
    )

    # AND old Answer from 2016
    make(Answer, **{
        'appuser': appuser,
        'id': 'vam_spb_incident_2016',
        'timestamp': datetime(2016, 4, 4, 0, 1, tzinfo=MSK),
        'question_id': 'vam_predostavili',
        'value_bool': False,
        'is_incident': True,
        'revoked': True,
        'uik': 9004,
        'role': 'psg',
        'uik_complaint_status': int16('отказ принять жалобу'),
        'tik_complaint_status': int16('ожидает модератора'),
        'tik_complaint_text': '123',
        'region': spb
    })

    # AND recent Answer
    make(Answer, **{
        'appuser': appuser,
        'id': 'vam_spb_incident',
        'timestamp': datetime(2024, 9, 11, 0, 1, tzinfo=MSK),
        'question_id': 'vam_predostavili',
        'value_bool': False,
        'is_incident': True,
        'revoked': True,
        'uik': 803,
        'role': 'psg',
        'uik_complaint_status': int16('отказ принять жалобу'),
        'tik_complaint_status': int16('ожидает модератора'),
        'tik_complaint_text': '123',
        'region': spb
    })

    # AND recent Answer
    make(Answer, **{
        'appuser': appuser,
        'id': 'vam_spb_ok',
        'timestamp': datetime(2024, 9, 11, 0, 2, tzinfo=MSK),
        'question_id': 'vam_predostavili',
        'value_bool': True,
        'is_incident': False,
        'revoked': False,
        'uik': 14,
        'role': 'psg',
        'uik_complaint_status': int16('не подавалась'),
        'tik_complaint_status': int16('ожидает модератора'),
        'tik_complaint_text': '123',
        'region': spb
    })

    # AND recent Answer
    make(Answer, **{
        'appuser': appuser,
        'id': 'vbros_a',
        'timestamp': datetime(2024, 9, 11, 0, 3, tzinfo=MSK),
        'question_id': 'vbros',
        'value_bool': True,
        'is_incident': False,
        'revoked': False,
        'uik': 7,
        'role': 'psg',
        'uik_complaint_status': int16('отказ принять жалобу'),
        'tik_complaint_status': int16('ожидает модератора'),
        'tik_complaint_text': '123',
        'region': msk
    })


    ######
    # WHEN user opens answers history
    page.goto(f"{live_server}/history")

    # THEN All answers should be visible
    expect(page.locator("time").filter(has_text="11 Sep 2024, 00:03")).to_be_visible()
    expect(page.locator("time").filter(has_text="11 Sep 2024, 00:02")).to_be_visible()
    expect(page.locator("time").filter(has_text="11 Sep 2024, 00:01")).to_be_visible()
    expect(page.locator("time").filter(has_text="04 Apr 2016, 00:01")).to_be_visible()

    ######
    # WHEN user clicks filter "complaint: yes"
    page.get_by_label("Complaint Filter").get_by_label("Yes").click()

    # THEN Answer 14 without complaint should be hidden
    expect(page.get_by_text("Санкт-Петербург UIK 14")).to_have_count(0)
    # AND 3 other answers with complaint should be visible
    expect(page.get_by_text("Санкт-Петербург UIK 803")).to_be_visible()
    expect(page.get_by_text("Москва UIK 7")).to_be_visible()
    expect(page.get_by_text("Санкт-Петербург UIK 9004")).to_be_visible()

    #######
    # WHEN user clicks filter "Include revoked"
    page.get_by_label("Include revoked").click()

    # THEN not revoked answer 7 should be visible
    expect(page.get_by_text("Москва UIK 7")).to_be_visible()
    # AND not revoked answer 14 should still be hidden, as it does not have complaint
    expect(page.get_by_text("Санкт-Петербург UIK 14")).to_have_count(0)
    # AND two other which have complaint but are revoked are hidden
    expect(page.get_by_text("Санкт-Петербург UIK 803")).to_have_count(0)
    expect(page.get_by_text("Санкт-Петербург UIK 9004")).to_have_count(0)

    ########
    # WHEN user clicks regions filter
    page.get_by_placeholder("Region: all").click()

    # AND click spb
    page.get_by_role("option", name="Санкт-Петербург").click()

    # THEN all answers should be hidden
    expect(page.get_by_text("Москва UIK 7")).to_have_count(0)
    # AND not revoked answer 14 should still be hidden, as it does not have complaint
    expect(page.get_by_text("Санкт-Петербург UIK 14")).to_have_count(0)
    # AND two other which have complaint but are revoked are hidden
    expect(page.get_by_text("Санкт-Петербург UIK 803")).to_have_count(0)
    expect(page.get_by_text("Санкт-Петербург UIK 9004")).to_have_count(0)
