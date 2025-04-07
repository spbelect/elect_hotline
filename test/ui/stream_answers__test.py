# -*- coding: utf-8 -*-
import re
import time

from datetime import datetime, date, timedelta
from collections import OrderedDict

import httpx
import pendulum
import pytest
import time_machine

from django.conf import settings
from django.core import mail
from django.urls import reverse
from django.test import TestCase
from django.test import override_settings
from django.utils.timezone import localtime, now
from model_bakery.baker import make
from playwright.sync_api import Playwright, Page, expect
from unittest.mock import Mock, patch, ANY

from ufo.models.base import int16
from ufo.models import (
    Region, Country, WebsiteUser, Election, Campaign, Organization, Contact, OrgBranch,
    WebsiteUser, QuizTopic, Question, Answer, MobileUser
)

from .. import base
from ..base import MSK, ru, spb, msk, uvicorn_server


# @pytest.mark.asyncio(scope="session")
@pytest.mark.uitest
@pytest.mark.django_db(transaction=True)
@time_machine.travel(datetime(2024, 9, 16, tzinfo=MSK), tick=False)
def stream_answers_scenario__test(uvicorn_server, spb, msk, page):
    # # GIVEN current user is logged in as test@example.com
    # with base.patch_auth():
    #     page.goto(f'{uvicorn_server}/auth/login/signed?auth_user=test@example.com')

    # AND quiz topic with 2 questions
    topic = make(QuizTopic, name='ДО НАЧАЛА ГОЛОСОВАНИЯ', questions=[
        make(Question, id='vam_predostavili', label='вам предоставили', type='YESNO'),
        make(Question, id='vbros', label='вброс', type='YESNO')
    ])

    # AND Mobile user
    appuser = make(MobileUser,
         id='123',
         # elections=[old_spb_election, guber_spb, president_elections]
    )

    # AND old Answer from 2016
    make(Answer, **{
        'appuser': appuser,
        'id': 'vam_spb_incident_2016',
        'timestamp': datetime(2016, 4, 4, 0, 1, tzinfo=MSK),
        'time_created': datetime(2016, 4, 4, 0, 1, tzinfo=MSK),
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
        'timestamp': datetime(2024, 9, 16, 0, 1, tzinfo=MSK),
        'time_created': datetime(2024, 9, 16, 0, 1, tzinfo=MSK),
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
        'timestamp': datetime(2024, 9, 16, 0, 2, tzinfo=MSK),
        'time_created': datetime(2024, 9, 16, 0, 2, tzinfo=MSK),
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
        'timestamp': datetime(2024, 9, 16, 0, 3, tzinfo=MSK),
        'time_created': datetime(2024, 9, 16, 0, 3, tzinfo=MSK),
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
    # WHEN user opens answers stream
    page.goto(f"{uvicorn_server}/answers/stream")

    # THEN three recent answers should be visible
    expect(page.locator("time").filter(has_text="16 Sep 2024, 00:03")).to_be_visible()
    expect(page.locator("time").filter(has_text="16 Sep 2024, 00:02")).to_be_visible()
    expect(page.locator("time").filter(has_text="16 Sep 2024, 00:01")).to_be_visible()
    # AND old answer should be hidden
    expect(page.locator("time").filter(has_text="04 Apr 2016, 00:01")).to_have_count(0)


    ########
    # WHEN user clicks regions filter
    page.get_by_placeholder("Region: all").click()

    # AND click spb
    page.get_by_role("option", name="Санкт-Петербург").click()

    # THEN las three spb answers should be visible
    expect(page.get_by_text("Санкт-Петербург UIK 14")).to_be_visible()
    expect(page.get_by_text("Санкт-Петербург UIK 803")).to_be_visible()
    expect(page.get_by_text("Санкт-Петербург UIK 9004")).to_be_visible()
    # AND msk answers should be hidden
    expect(page.get_by_text("Москва UIK 7")).to_have_count(0)


    #####
    # WHEN new spb answer is submitted to mobile api
    response = httpx.post(f'{uvicorn_server}/api/v4/answers/', json={
        'app_id': '123',
        'id': '456',
        'timestamp': '2025-03-30T23:59:00Z',
        'question_id': 'vbros',
        'value': True,
        'is_incident': True,
        'revoked': False,
        'uik': 99,
        'role': 'psg',
        'uik_complaint_status': 'отказ принять жалобу',
        'tik_complaint_status': 'отправляется модератору',
        'tik_complaint_text': '123',
        'region_id': spb.id
    })

    # THEN response status should be HTTP_201_CREATED
    assert response.status_code is 201

    # AND new answer should be visible in the stream
    expect(page.get_by_text("Санкт-Петербург UIK 99")).to_be_visible()


    #####
    # WHEN new msk answer is submitted to mobile api
    response = httpx.post(f'{uvicorn_server}/api/v4/answers/', json={
        'app_id': '123',
        'id': '789',
        'timestamp': '2025-03-30T23:59:00Z',
        'question_id': 'vbros',
        'value': True,
        'is_incident': True,
        'revoked': False,
        'uik': 1,
        'role': 'psg',
        'uik_complaint_status': 'отказ принять жалобу',
        'tik_complaint_status': 'отправляется модератору',
        'tik_complaint_text': '123',
        'region_id': msk.id
    })

    # THEN response status should be HTTP_201_CREATED
    assert response.status_code is 201

    # AND new answer should NOT be visible in the stream
    expect(page.get_by_text("Москва UIK 1")).to_have_count(0)
