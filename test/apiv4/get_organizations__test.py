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
    Region, Country, WebsiteUser, Election, Campaign, Organization, Contact, OrgBranch
)
from .. import base


class GetOrganizationsTest(django.test.TestCase):
    # Upon request of organizations in given region, JSON should be returned, including
    # organization name and contacts.

    def setUp(self):
        # GIVEN Country with 2 regions
        ru = make(Country, id='ru', name='Russia')

        spb = make(Region, id='ru_78', name='Saint-Petersburg', country=ru, utc_offset=3)
        msk = make(Region, id='ru_11', name='Moscow', country=ru, utc_offset=3)
        
        # AND organization
        org = make(Organization, id='organization-id1', name='Saint-Petersburg Observers')

        # AND org contacts include phone and telegram channel
        make(Contact,
            organization_id='organization-id1',
            name='public chat',
            value='http://t.me/obs',
            type='tg'
        )
        make(Contact,
            organization_id='organization-id1',
            name='Call center',
            value='8666',
            type='ph'
        )

        # AND 2 regional org branches including region spb (78) and msk
        make(OrgBranch,
             organization=org,
             region=spb,
             uik_ranges=[[1,100], [1305, 1310]]
        )
        make(OrgBranch,
             organization=org,
             region=msk,
        )

        # AND organization
        org_msk = make(Organization, id='organization-id2', name='Moscow Observers')
        # AND 1 regional org branch in Moscow
        make(OrgBranch,
             organization=org_msk,
             region=msk,
        )

    def test_get_organizations_success(self):
        # WHEN user GETs spb (ru_78) organizations
        response = self.client.get('/api/v4/ru/regions/78/organizations/')

        # THEN response status should be HTTP_200_OK
        assert response.status_code is 200

        # AND campaigns, organizations and elections should be returned
        assert response.json() == [{
            'id': 'organization-id1',
            'name': 'Saint-Petersburg Observers',
            'contacts': [
                {
                    'name': 'Call center',
                    'type': 'ph',
                    'value': '8666',
                },
                {
                    'name': 'public chat',
                    'type': 'tg',
                    'value': 'http://t.me/obs',
                },
            ],
        }]
