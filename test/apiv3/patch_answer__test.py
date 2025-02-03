# -*- coding: utf-8 -*-

from os import remove
from os.path import basename, dirname, join
from subprocess import call

import django.test
from django.core import mail
from django.conf import settings
from django.urls import reverse
from django.test import override_settings
from django.utils.timezone import now
from unittest.mock import Mock, patch, ANY
from model_bakery.baker import make

from rest_framework.serializers import ValidationError
from rest_framework.status import HTTP_201_CREATED
# from nose.plugins.attrib import attr

from ufo.models import (
    Answer, Country, MobileUser, QuizTopic, Question, TopicQuestions, Region,
    TikSubscription, Campaign, Tik, int16
)


@override_settings(
    TIK_EMAIL_MODERATION=False,
    FAKE_TIK_EMAILS=False,
    ADMIN_EMAIL='admin@example.com'
)
class PatchAnswerSuccessTest(django.test.TestCase):
    # При получении запроса обновления (PATCH) ответа, оно должно быть обновлено в БД.

    def setUp(self):
        # GIVEN Country with region
        ru = make(Country, id='ru', name='Россия')
        spb = make(Region, id='ru_78', name='Санкт-Петербург', country=ru, utc_offset=3)

        # AND App user with app_id
        make(MobileUser, app_id='123', email='appuser@ya.ru', id=1)

        # AND federal campaign
        campaign = make(Campaign, election__date=now())
        # AND Tik
        tik = make(Tik, region=spb, name='tiktik', uik_ranges='[[0, 9999]]', email='tik@example.com')
        # AND tik member
        make(
            TikSubscription, tik=tik, email='tikmember@example.com', organization=campaign.organization
        )
        # AND quiz topic with one YESNO question
        topic = make(QuizTopic, name='ДО НАЧАЛА ГОЛОСОВАНИЯ', questions=[
            make(Question, id='question_id1', label='вброс', type='YESNO')
        ])
    
    def test_put_event_success(self):
        # GIVEN existing answer with default tik\uik_complaint_status
        make(
            Answer, 
            id = 'answer_id1', 
            appuser_id = 1, 
            question_id = 'question_id1', 
            uik = 803, 
            region_id = 'ru_78',
            #uik_complaint_status = 'none', 
            #tik_complaint_status = 'none', 
            is_incident = False, 
            revoked = False,
            role = 'psg'
        )
        
        # WHEN user sends PATCH request for existing answer with new tik\uik_complaint_status
        response = self.client.patch('/api/v3/answers/answer_id1/', data={
            'app_id': '123',
            'revoked': True,
            'uik_complaint_status': 'получено неудовлетворительное решение',
            'tik_complaint_status': 'отправляется модератору',
            'tik_complaint_text': 'жалоба'
        }, content_type='application/json')

        # THEN response status should be 200
        self.assertEqual(response.status_code, 200)

        # AND existing answer should get updated in db
        assert list(Answer.objects.values()) == [{
            'time_created': ANY,
            #'modified': ANY,
            'is_incident': False,
            'question_id': 'question_id1',
            'region_id': 'ru_78',
            'timestamp': ANY,
            'uik': 803,
            'role': 'psg',
            'uik_complaint_status': int16('получено неудовлетворительное решение'),  # updated
            'tik_complaint_status': int16('email отправлен'),   # updated
            'tik_complaint_text': 'жалоба',   # updated
            'revoked': True,  # updated
            'time_tik_email_request_created': ANY,
            'value_bool': None,
            'value_int': None,
            'banned': False,
            'id': ANY,
            'timestamp': ANY,
            'appuser_id': 1,
            'operator_id': None
        }]
        
        # AND 1 email sent
        assert len(mail.outbox) == 1
        # to tik
        assert mail.outbox[0].to == ['tik@example.com']
        # AND admin and tik member in bcc
        assert set(mail.outbox[0].bcc) == set(['tikmember@example.com', 'appuser@ya.ru'])

    
