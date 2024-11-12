# -*- coding: utf-8 -*-

from datetime import date, timedelta
from os import remove
from os.path import basename, dirname, join
from subprocess import call

from django.conf import settings
from django.urls import reverse
from django.test import TestCase
from django.test import override_settings
from unittest.mock import Mock, patch, ANY
from model_bakery.baker import make

from rest_framework.serializers import ValidationError
from rest_framework.status import HTTP_201_CREATED
# from nose.plugins.attrib import attr

from ufo.models import (
    Answer, MobileUser, QuizTopic, Question, TopicQuestions, Region, int16, Election,
    ElectionMobileUsers
)

from ..base import BaseTestCase


class PostAnswerSuccessTest(BaseTestCase):
    # При получении валидного ответа, оно должно быть сохранено в БД.

    def setUp(self):
        # GIVEN App user with app_id
        make(MobileUser, app_id='123', id=1)
        # AND region spb
        spb = make(Region, id='ru_78', name='Sankt-Peterburg')
        # AND quiztopic win one YESNO question
        topic = make(QuizTopic, name='ДО НАЧАЛА ГОЛОСОВАНИЯ', questions=[
            make(Question, id='question_id1', label='вброс', type='YESNO')
        ])
        # AND active federal election
        make(Election, id=1, date=date.today() + timedelta(days=30), region=None)
        # AND 2 active campaigns in spb
        make(Election, id=2, date=date.today(), region=spb)
        make(Election, id=3, date=date.today(), region=spb)
        # AND active election in other region
        make(Election, id=4, date=date.today(), region__name='Other')
        
        # AND old fedral election
        make(Election, date=date(2009, 1, 1), region=None)
        # AND old election in spb
        make(Election, date=date(2007, 1, 1), region=spb)
        

    def test_post_answer_success(self):
        # WHEN user POSTs valid answer
        response = self.client.post('/api/v3/answers/', data={
            'app_id': '123',
            'id': '456',
            'timestamp': '2016-12-30T23:59:00Z',
            'question_id': 'question_id1',
            'value': True,
            'is_incident': True,
            'revoked': False,
            'uik': 803,
            'role': 'psg',
            'uik_complaint_status': 'отказ принять жалобу',
            'tik_complaint_status': 'отправляется модератору',
            'tik_complaint_text': '123',
            'region': 'ru_78'})

        # THEN response status should be HTTP_201_CREATED
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        # AND one answer should get created
        assert list(Answer.objects.values()) == [{
            'time_created': ANY,
            #'modified': ANY,
            'is_incident': True,
            'question_id': 'question_id1',
            'region_id': 'ru_78',
            'timestamp': ANY,
            'uik': 803,
            'role': 'psg',
            'uik_complaint_status': int16('отказ принять жалобу'),
            'tik_complaint_status': int16('ожидает модератора'),
            'tik_complaint_text': '123',
            'time_tik_email_request_created': ANY,
            'value_bool': True,
            'value_int': None,
            'revoked': False,
            'banned': False,
            'id': '456',
            'timestamp': ANY,
            'appuser_id': 1,
            'operator_id': None
        }]

        # AND mobile user should be added to active election in Sankt-Peterburg and Russia.
        streamers = ElectionMobileUsers.objects.order_by('election')
        assert list(streamers.values('mobileuser', 'election', 'election__region')) == [
            {
                'mobileuser': 1,
                'election': '1',
                'election__region': None
            },
            {
                'mobileuser': 1,
                'election': '2',
                'election__region': 'ru_78'
            },
            {
                'mobileuser': 1,
                'election': '3',
                'election__region': 'ru_78'
            },
        ]
