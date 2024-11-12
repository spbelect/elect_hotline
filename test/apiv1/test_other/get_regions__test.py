## -*- coding: utf-8 -*-

#from datetime import datetime
#from collections import OrderedDict

#from django.conf import settings
#from django.urls import reverse
#from django.test import TestCase
#from django.test import override_settings
#from django.utils.timezone import localtime, now
#from unittest.mock import Mock, patch, ANY
#from model_bakery.baker import make
#
#from rest_framework.serializers import ValidationError, DateTimeField
##from rest_framework.settings import api_settings
#from rest_framework.status import HTTP_200_OK
## from nose.plugins.attrib import attr

#from ufo.models import Region, User
#from ..base import BaseTestCase


#class GetRegionsSuccessTest(BaseTestCase):
    ## При запросе списка регионов должен возвращаться JSON список

    #def setUp(self):
        ## GIVEN User with app_id
        ##make(User, app_ids=['123'])

        ## GIVEN Region
        #make(Region, name='spb', external_id=78, sos_phone='999', tg_channel='xx')

    #def test_get_regions_success(self):
        ## WHEN user GETs regions list
        #response = self.client.get(reverse('api_regions'))

        ## THEN response status should be HTTP_200_OK
        #self.assertEqual(response.status_code, HTTP_200_OK)

        ## AND one region should be returned
        #assert response.data == [OrderedDict(id='78', name='spb', sos_phone='999', tg_channel='xx')]
