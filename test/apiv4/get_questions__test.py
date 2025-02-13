
from datetime import datetime, date, timedelta, timezone
from collections import OrderedDict
from unittest.mock import Mock, patch, ANY

import ninja.testing
import django.test
import pendulum

from django.conf import settings
from django.urls import reverse
from django.test import override_settings
from django.utils.timezone import localtime, now
from model_bakery.baker import make

import ufo.api
from ufo.models import (
    Region, Country, WebsiteUser, Election, Campaign, Organization, TopicQuestions, QuizTopic
)
from .. import base


class GetQuestionsSuccessTest(django.test.TestCase):
    # Upon request of questions for given country, JSON has to be returned with
    # topics and questions sorted by sortorder.
    
    def setUp(self):
        # GIVEN Country
        ru = make(Country, id='ru', name='Russia')

        # AND topic
        make(QuizTopic, id='a2', name='BEFORE VOTING STARTS', country=ru, sortorder=2)

        # AND another one
        na_vyezd = make(QuizTopic, id='a1', name='OUTDOOR VOTING', country=ru, sortorder=1)
        
        # AND 3 YESNO questions
        make(TopicQuestions, question__id='3', topic=na_vyezd, question__type='YESNO', sortorder=3)
        make(TopicQuestions, question__id='2', topic=na_vyezd, question__type='YESNO', sortorder=2)
        make(TopicQuestions, question__id='1', topic=na_vyezd, question__type='YESNO', sortorder=1,
             question__incident_conditions={"answer_equals_to": False})


    def test_get_questions_success(self):
        # WHEN user GETs questions list
        response = self.client.get('/api/v4/ru/questions/')

        # THEN response status should be HTTP_200_OK
        assert response.status_code is 200

        # AND questions grouped by topic should be returned, sorted by sortorder
        assert response.json() == [
        {
            'id': 'a1',
            'name': 'OUTDOOR VOTING',
            'questions': [
                {
                    'id': '1',
                    'type': 'YESNO',
                    'advice_text': None,
                    'elect_flags': None,
                    'label': ANY,
                    'fz67_text': None,
                    'example_uik_complaint': None,
                    'limiting_questions': None,
                    'incident_conditions': {"answer_equals_to": False}
                },
                {
                    'id': '2',
                    'type': 'YESNO',
                    'advice_text': None,
                    'elect_flags': None,
                    'label': ANY,
                    'fz67_text': None,
                    'example_uik_complaint': None,
                    'limiting_questions': None,
                    'incident_conditions': None
                },
                {
                    'id': '3',
                    'type': 'YESNO',
                    'advice_text': None,
                    'elect_flags': None,
                    'label': ANY,
                    'fz67_text': None,
                    'example_uik_complaint': None,
                    'limiting_questions': None,
                    'incident_conditions': None
                },
            ],
        },
        {
            'id': 'a2',
            'name': 'BEFORE VOTING STARTS',
            'questions': [],
        }
    ]
