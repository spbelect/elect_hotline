# -*- coding: utf-8 -*-

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

from ufo.models import Answer, MobileUser

from ..base import BaseTestCase


class PostProfileEventSuccessTest(BaseTestCase):
    # При получении валидного события, оно должно быть сохранено в БД.

    def setUp(self):
        # GIVEN App user with app_id
        make(MobileUser, app_id='123', id=1)

    def test_post_profile_event_success(self):
        # WHEN user POSTs valid event data
        response = self.client.post('/api/v3/userprofile/', data=dict(
            app_id = '123', 
            first_name = 'First',
            last_name = 'Last',
            phone = '567',
            email = 'x@ya.ru',
            telegram = 'ttt',
        ))

        # THEN response status should be 200
        self.assertEqual(response.status_code, 200)

        # AND MobileUser should get updated
        self.assertEqual(list(MobileUser.objects.values()), [dict(
            time_created=ANY,
            #time_modified=ANY,
            id=1,
            app_id='123',
            first_name = 'First',
            last_name = 'Last',
            middle_name=None,
            phone = '567',
            email = 'x@ya.ru',
            telegram = 'ttt',
            region_id=None,
            role=None,
            time_last_answer=ANY,
            uik=None
        )])
