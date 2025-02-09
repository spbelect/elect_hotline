# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta, timezone
from collections import OrderedDict
from unittest.mock import Mock, patch, ANY

import ninja.testing
import django.test
import pendulum
import time_machine

from django.conf import settings
from django.urls import reverse
from django.test import override_settings
from django.utils.timezone import localtime, now
from model_bakery.baker import make
from ninja.testing import TestClient

import ufo.api
from ufo.models import (
    Region, Country, WebsiteUser, Election, Campaign, Organization, Contact, OrgBranch
)
from .. import base


@time_machine.travel(datetime(2024, 9, 11, 0, 0, tzinfo=timezone.utc))
class GetElectionsSuccessTest(django.test.TestCase):
    # Upon request of elections in given region, JSON should be returned, including
    # municipal, regional and federal elections.

    def setUp(self):
        # GIVEN Country with 2 regions
        ru = make(Country, id='ru', name='Russia')

        spb = make(Region, id='ru_78', name='Saint-Petersburg', country=ru, utc_offset=3)
        msk = make(Region, id='ru_11', name='Moscow', country=ru, utc_offset=3)
        
        # AND 2 old Elections
        make(Election, 
            id='election-id-fed-2013',  name='Federal elections 2013', date=date(2013, 4, 4),
        )
        old_spb_election = make(Election, 
            id='election-id-spb-2013',  name='Spb elections 2013', date=date(2013, 4, 4), region=spb
        )
        
        # AND actual federal Election
        make(Election, 
            id='election-id-fed-actual', 
            name='Federal parliament elections',
            date = date(2024, 9, 21),
            country = ru
        )

        # AND actual regional Election
        spb_election = make(Election, 
            id='election-id-spb-actual', 
            name='Saint-Petersburg governor elections',
            region=spb,
            date = date(2024, 9, 21),
        )


    def test_get_elections_success(self):
        # WHEN user GETs spb (ru_78) elections
        response = self.client.get('/api/v4/ru/regions/78/elections/')

        # THEN response status should be HTTP_200_OK
        assert response.status_code is 200

        # AND campaigns, organizations and elections should be returned
        assert response.json() == [
            {
                'name': 'Federal parliament elections',
                'flags': None,
                'region': None,
                'munokrug': None,
                'date': '2024-09-21',
            },
            {
                'name': 'Saint-Petersburg governor elections',
                'flags': None,
                'region': 'ru_78',
                'munokrug': None,
                'date': '2024-09-21',
            },
        ]
