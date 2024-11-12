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

#from ufo.models import InputEvent User
#from ..base import BaseTestCase


#class GetEventsSuccessTest(BaseTestCase):
    ## При запросе списка событий должен возвращаться JSON список

    #def setUp(self):
        ## GIVEN User with app_id
        ##make(User, app_ids=['123'])

        #self.event = makeInputEvent
            #data={
                #'app_id': '123',
                #'timestamp': '2018-02-28T17:22:41.705646+03:00'
            #},
            #timestamp='2018-02-28T17:22:41.705646+03:00',
            #id='99735d7a-be41-466b-a978-49ffc323d07e',
        #)

    #def test_get_event_success(self):
        ## WHEN user GETs events list
        #response = self.client.get(reverse('api_event'))

        ## THEN response status should be HTTP_200_OK
        #self.assertEqual(response.status_code, HTTP_200_OK)

        ## AND oneInputEventshould be returned
        #assert response.data == [OrderedDict(
            #id='99735d7a-be41-466b-a978-49ffc323d07e',
            #timestamp='2018-02-28T17:22:41.705646+03:00',
            #created=ANY,
            #modified=ANY,
            #deleted=False,
            #user=None,
            #userprofile=None,
            #app_id='123',
        #)]
