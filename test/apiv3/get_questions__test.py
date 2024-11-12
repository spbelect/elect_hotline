# -*- coding: utf-8 -*-

from datetime import datetime
from collections import OrderedDict

from django.conf import settings
from django.urls import reverse
from django.test import TestCase
from django.test import override_settings
from django.utils.timezone import localtime, now
from unittest.mock import Mock, patch, ANY
from model_bakery.baker import make

from rest_framework.serializers import ValidationError, DateTimeField
#from rest_framework.settings import api_settings
from rest_framework.status import HTTP_200_OK
# from nose.plugins.attrib import attr

from ufo.models import Region, WebsiteUser, QuizTopic, Question, TopicQuestions
from ..base import BaseTestCase


class GetQuestionsSuccessTest(BaseTestCase):
    # При запросе вопросов заданной страны должен возвращаться JSON список тематических
    # секций анкеты, содержащих список вопросов, отсортированных в порядке возрастания
    # значения sortorder в бд.
    
    def setUp(self):
        # GIVEN User with app_id
        #make(User, app_ids=['123'])

        # GIVEN topic
        make(QuizTopic, id='a2', name='ДО НАЧАЛА ГОЛОСОВАНИЯ', sortorder=2)

        # AND another one
        na_vyezd = make(QuizTopic, id='a1', name='НА ВЫЕЗДНОМ', sortorder=1)
        
        # AND 3 YESNO questions
        make(TopicQuestions, question__id='3', topic=na_vyezd, question__type='YESNO', sortorder=3)
        make(TopicQuestions, question__id='2', topic=na_vyezd, question__type='YESNO', sortorder=2)
        make(TopicQuestions, question__id='1', topic=na_vyezd, question__type='YESNO', sortorder=1,
             question__incident_conditions={"answer_equals_to": False})


    def test_get_questions_success(self):
        # WHEN user GETs regions list
        response = self.client.get('/api/v3/ru/questions/')

        # THEN response status should be HTTP_200_OK
        self.assertEqual(response.status_code, HTTP_200_OK)

        # AND questions grouped by topic should be returned, sorted by sortorder
        assert response.data == [
        {
            'id': 'a1',
            'name': 'НА ВЫЕЗДНОМ',
            'questions': [
                {
                    'id': '1',
                    'type': 'YESNO',
                    'label': ANY,
                    'fz67_text': None,
                    'example_uik_complaint': None,
                    'visible_if': {
                        'elect_flags': [],
                        'limiting_questions': {}
                    },
                    'incident_conditions': {"answer_equals_to": False}
                },
                {
                    'id': '2',
                    'type': 'YESNO',
                    'label': ANY,
                    'fz67_text': None,
                    'example_uik_complaint': None,
                    'visible_if': {
                        'elect_flags': [],
                        'limiting_questions': {}
                    },
                    'incident_conditions': {}
                },
                {
                    'id': '3',
                    'type': 'YESNO',
                    'label': ANY,
                    'fz67_text': None,
                    'example_uik_complaint': None,
                    'visible_if': {
                        'elect_flags': [],
                        'limiting_questions': {}
                    },
                    'incident_conditions': {}
                },
            ],
        },
        {
            'id': 'a2',
            'name': 'ДО НАЧАЛА ГОЛОСОВАНИЯ',
            'questions': [],
        }
    ]
