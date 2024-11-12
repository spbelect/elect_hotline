# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from collections import OrderedDict

import pendulum
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

from ufo.models import (
    Region, Country, WebsiteUser, Election, Campaign, Organization, Contact, OrgBranch
)
from ..base import BaseTestCase


class GetElectionsSuccessTest(BaseTestCase):
    # При запросе выборов должен возвращаться JSON с выборами, координаторами, кампаниями

    def setUp(self):
        # GIVEN Country with 2 regions
        ru = make(Country, id='ru', name='Россия')

        spb = make(Region, id='ru_78', name='Санкт-Петербург', country=ru, utc_offset=3)
        msk = make(Region, id='ru_11', name='Москва', country=ru, utc_offset=3)
        
        # AND 2 old Elections
        make(Election, 
            id='election-id-fed-2013',  name='Федеральные Выборы 2013', date=date(2013, 4, 4),
        )
        old_spb_election = make(Election, 
            id='election-id-spb-2013',  name='Cпб Выборы 2013', date=date(2013, 4, 4), region=spb
        )
        
        # AND actual federal Election
        make(Election, 
            id='election-id-fed-actual', 
            name='Федеральные Выборы', 
            date = date.today() + timedelta(days=10),
        )
        
        # AND actual regional Election
        spb_election = make(Election, 
            id='election-id-spb-actual', 
            name='Cпб Выборы', 
            region=spb,
            date = date.today() + timedelta(days=10),
        )
        
        # AND organization with telegram channel
        org = make(Organization, id='organization-id1', name='Наблюдатели петербурга')
        make(Contact, 
            organization_id='organization-id1', 
            name='общийчат1', 
            value='http://t.me/obs',
            type='tg'
        )
        
        # AND 2 org branches
        make(OrgBranch,
             organization=org,
             region=spb,
             uik_ranges=[[1,100], [1305, 1310]]
        )
        make(OrgBranch,
             organization=org,
             region=msk,
        )
        
        # AND actual regional campaign with phone and tg channel
        camp = make(Campaign, 
            id='campaign-id-actual', 
            organization_id='organization-id1', 
            election=spb_election
        )
        make(Contact, 
            organization_id='organization-id1', 
            campaign=camp,
            name='Коллц', 
            value='8666', 
            type='ph'
        )
        make(Contact, 
            organization_id='organization-id1', 
            campaign=camp,
            name='чат1', 
            value='http://t.me/chat1',
            type='tg'
        )
        
        # AND old regional campaign
        camp = make(Campaign, 
            id='campaign-id-2013', 
            organization_id='organization-id1', 
            election=old_spb_election
        )


    def test_get_elections_success(self):
        # WHEN user GETs elections
        response = self.client.get('/api/v3/ru_78/elections/')

        # THEN response status should be HTTP_200_OK
        self.assertEqual(response.status_code, HTTP_200_OK)

        # AND campaigns, organizations and elections should be returned
        assert response.data == [
            {
                'name': 'Федеральные Выборы', 
                'flags': [''], 
                'region': None,
                'date': date.today() + timedelta(days=10),
                'coordinators': []
            },
            {
                'name': 'Cпб Выборы', 
                'flags': [''], 
                'region': 'ru_78',
                'date': date.today() + timedelta(days=10),
                'coordinators': [{
                    'org_id': 'organization-id1',
                    'org_name': 'Наблюдатели петербурга',
                    'contacts': [
                        {'name': 'общийчат1', 'type': 'tg', 'value': 'http://t.me/obs'}
                    ],
                    'campaign': {
                        'id': 'campaign-id-actual',
                        'contacts': [
                            {'name': 'Коллц', 'type': 'ph', 'value': '8666'},
                            {'name': 'чат1', 'type': 'tg', 'value': 'http://t.me/chat1'}
                        ],
                        'uik_ranges': [[1,100], [1305, 1310]]
                    }
                }],
            },
        ]
