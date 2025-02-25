# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta, timezone as tz
from os import remove
from os.path import basename, dirname, join
from subprocess import call

import django.test
import time_machine

from django.conf import settings
from django.urls import reverse
from django.test import override_settings
from unittest.mock import Mock, patch, ANY
from model_bakery.baker import make


from ufo.models import (
    Answer, MobileUser, QuizTopic, Question, TopicQuestions, Region, int16, Election,
    ElectionMobileUsers, Munokrug
)


@time_machine.travel(datetime(2024, 6, 1, tzinfo=tz.utc), tick=False)
class PostInvalidAnswerTest(django.test.TestCase):
    # Upon receiving invalid POST answer request, error should be returned

    def setUp(self):
        # GIVEN App user with app_id
        make(MobileUser, app_id='123', id=1)

        # AND region spb
        spb = make(Region, id='ru_78', name='Sankt-Peterburg')

        # AND Munokrug
        mo1 = make(Munokrug, name='MO 1', region=spb, uik_ranges='[[1,900]]')

        # AND quiztopic win one YESNO question
        topic = make(QuizTopic, name='ДО НАЧАЛА ГОЛОСОВАНИЯ', questions=[
            make(Question, id='question_id1', label='вброс', type='YESNO')
        ])

        # AND active federal election
        make(Election, name="Federal election",
             id=1, date=date.today() + timedelta(days=30), region=None)
        # AND regional election in spb
        make(Election, name="Regional spb election",
             id=2, date=date.today(), region=spb)
        # AND municipal election in spb
        make(Election, name="Municipal spb MO 1 election",
             id=3, date=date.today(), region=spb, munokrug=mo1)

        # AND active election in other region
        make(Election, id=4, date=date.today(), region__name='Other')
        
        # AND old fedral election
        make(Election, date=date(2009, 1, 1), region=None)
        # AND old election in spb
        make(Election, date=date(2007, 1, 1), region=spb)
        

    def test_post_answer_invalid(self):
        # WHEN user POSTs invalid answer
        response = self.client.post('/api/v4/answers/', data={
            'app_id': '123',
            'id': '456',
            'timestamp': '2016-12-30T23:59:00Z',
            'question_id': 'non_existing',   # invalid question
            'value': True,
            'is_incident': True,
            'revoked': False,
            'uik': 803,
            'role': 'psg',
            'uik_complaint_status': 'отказ принять жалобу',
            'tik_complaint_status': 'отправляется модератору',
            'tik_complaint_text': '123',
            'region_id': 'ru_78'}, content_type='application/json')

        # THEN response status should be 422
        assert response.status_code == 422

        # AND reponse body has error message
        assert response.json() == {
            'detail': [
                {
                    'ctx': {
                        'error': 'No Question with id non_existing found',
                    },
                    'loc': [
                        'body',
                        'data',
                        'question_id',
                    ],
                    'msg': 'Value error, No Question with id non_existing found',
                    'type': 'value_error',
                },
            ],
        }

        # AND no answer should get created
        assert list(Answer.objects.values()) == []

        # AND mobile user should not be added to active election.
        streamers = ElectionMobileUsers.objects.order_by('election')
        assert list(streamers.values('mobileuser', 'election__name', 'election__region')) == []
