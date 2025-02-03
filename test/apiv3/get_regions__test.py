# -*- coding: utf-8 -*-

from datetime import datetime
from collections import OrderedDict

import django.test
from django.conf import settings
from django.urls import reverse
from django.test import override_settings
from django.utils.timezone import localtime, now
from unittest.mock import Mock, patch, ANY
from model_bakery.baker import make

from rest_framework.serializers import ValidationError, DateTimeField
#from rest_framework.settings import api_settings
from rest_framework.status import HTTP_200_OK
# from nose.plugins.attrib import attr

from ufo.models import Region, WebsiteUser, Tik, Munokrug, Country


class GetRegionsSuccessTest(django.test.TestCase):
    # При запросе блокформ должен возвращаться JSON список

    def setUp(self):
        # GIVEN User with app_id
        #make(User, app_ids=['123'])

        # GIVEN 2 Regions
        ru = make(Country, id='ru', name="Russia")
        lenobl = make(Region, id='ru_47', name='Лен. обл.', country=ru)
        spb = make(Region, id='ru_78', name='Spb', country=ru)

        # AND munokrug
        make(Munokrug, id='123', name='mo xz gde', uik_ranges="[[1,100], [4010, 4055]]", region=lenobl,
            ikmo_email='lol@x.ru',
            ikmo_phone='78796',
            ikmo_address='leninsky')
        # AND tik
        make(Tik, id='tik-x', name='Tik kingiseppskogo rayona', uik_ranges="[[21,800]]", region=lenobl,
            email='xx@x.ru',
            phone='6463',
            address='street')


    def test_get_regions_success(self):
        # WHEN user GETs regions list
        response = self.client.get('/api/v3/ru/regions/')

        # THEN response status should be HTTP_200_OK
        self.assertEqual(response.status_code, HTTP_200_OK)

        # AND regions be returned
        assert response.data == {
            'ru_47': {
                'id': 'ru_47',
                'name': 'Лен. обл.',
                'tiks': [
                    {
                        'id': 'tik-x',
                        'uik_ranges': [[21,800]],
                        'name': 'Tik kingiseppskogo rayona',
                        'email': 'xx@x.ru',
                        'phone': '6463',
                        'address': 'street'
                    },
                ],
                'munokruga': [
                    {
                        'id': '123',
                        'uik_ranges': [[1,100], [4010, 4055]],
                        'name': 'mo xz gde',
                        'ikmo_email': 'lol@x.ru',
                        'ikmo_phone': '78796',
                        'ikmo_address': 'leninsky'
                    },
                ],
            },
            'ru_78': {
                'id': 'ru_78',
                'name': 'Spb',
                'tiks': [],
                'munokruga': [],
            }
        }
