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
from model_bakery.baker import make
from playwright.sync_api import Playwright, Page, expect
from unittest.mock import Mock, patch, ANY

from rest_framework.serializers import ValidationError, DateTimeField
#from rest_framework.settings import api_settings
from rest_framework.status import HTTP_200_OK
# from nose.plugins.attrib import attr

from ufo.models.base import int16
from ufo.models import (
    Region, Country, WebsiteUser, Election, Campaign, Organization, Contact, OrgBranch,
    WebsiteUser, QuizTopic, Question, Answer, MobileUser
)
from ..base import BaseTestCase, patch_auth, MSK, ru, spb, msk



# @pytest.fixture
# def auth():
#     def authenticate(user):
#
#     return Fruit("apple")
#


# @login('test@example.com')
@pytest.mark.uitest
def filter_history_scenario__test(spb, msk, live_server, page):
    # GIVEN current user is logged in as test@example.com
    with patch_auth():
        page.goto(f'{live_server}/auth/login/?auth_user=test@example.com')

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
         id='123',
         elections=[
            old_spb_election, guber_spb, president_elections]
    )

    # AND old Answer from 2013
    make(Answer, **{
        'appuser': appuser,
        'id': 'vam_spb_incident_2013',
        'timestamp': datetime(2013, 4, 4),
        'question_id': 'vam_predostavili',
        'value_bool': False,
        'is_incident': True,
        'revoked': False,
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
        'timestamp': now(),
        'question_id': 'vam_predostavili',
        'value_bool': False,
        'is_incident': True,
        'revoked': False,
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
        'timestamp': now(),
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
        'timestamp': now(),
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
    # WHEN user opens answers feed
    page.goto(f"{live_server}/feed/answers/")

    # THEN 3 recent answers should be visible
    expect(page.get_by_text("Санкт-Петербург УИК 14")).to_be_visible()
    expect(page.get_by_text("Санкт-Петербург УИК 803")).to_be_visible()
    expect(page.get_by_text("Москва УИК 7")).to_be_visible()
    # AND one old answer hidden
    expect(page.get_by_text("Санкт-Петербург УИК 9004")).to_have_count(0)

    # WHEN user clicks filter Жалоба подавалась
    page.get_by_label("Фильтр жалоб").get_by_label("Жалоба подавалась").click()

    # THEN Answer 14 without complaint should be hidden
    expect(page.get_by_text("Санкт-Петербург УИК 14")).to_have_count(0)
    # AND 3 other answers with complaint should be visible
    expect(page.get_by_text("Санкт-Петербург УИК 803")).to_be_visible()
    expect(page.get_by_text("Москва УИК 7")).to_be_visible()
    expect(page.get_by_text("Санкт-Петербург УИК 9004")).to_have_count(0)


    # WHEN user clicks filter Только инциденты
    page.get_by_label("Фильтр инцидентов").click()
    page.get_by_label("Фильтр инцидентов").get_by_label("Только инциденты").click()

    # THEN only Answer 803 with incident True should be visible
    expect(page.get_by_text("Санкт-Петербург УИК 803")).to_be_visible()
    # AND two others are hidden
    expect(page.get_by_text("Санкт-Петербург УИК 14")).to_have_count(0)
    expect(page.get_by_text("Москва УИК 7")).to_have_count(0)
    expect(page.get_by_text("Санкт-Петербург УИК 9004")).to_have_count(0)


    ######
    # WHEN user opens answers history
    page.goto(f"{live_server}/history/")

    # THEN all 4 answers should be visible
    expect(page.get_by_text("Санкт-Петербург УИК 14")).to_be_visible()
    expect(page.get_by_text("Санкт-Петербург УИК 803")).to_be_visible()
    expect(page.get_by_text("Санкт-Петербург УИК 9004")).to_be_visible()
    expect(page.get_by_text("Москва УИК 7")).to_be_visible()
    #
    # # WHEN user clicks filter Жалоба подавалась
    # page.get_by_label("Фильтр жалоб").get_by_label("Жалоба подавалась").click()
    #
    # # THEN Answer 14 without complaint should be hidden
    # expect(page.get_by_text("Санкт-Петербург УИК 14")).to_have_count(0)
    # # AND two other answers with complaint should be visible
    # expect(page.get_by_text("Санкт-Петербург УИК 803")).to_be_visible()
    # expect(page.get_by_text("Москва УИК 7")).to_be_visible()
    #
    #
    # # WHEN user clicks filter Только инциденты
    # page.get_by_label("Фильтр инцидентов").click()
    # page.get_by_label("Фильтр инцидентов").get_by_label("Только инциденты").click()
    #
    # # THEN only Answer 803 with incident True should be visible
    # expect(page.get_by_text("Санкт-Петербург УИК 803")).to_be_visible()
    # # AND two others are hidden
    # expect(page.get_by_text("Санкт-Петербург УИК 14")).to_have_count(0)
    # expect(page.get_by_text("Москва УИК 7")).to_have_count(0)

