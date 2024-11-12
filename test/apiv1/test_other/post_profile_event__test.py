## -*- coding: utf-8 -*-

#from os import remove
#from os.path import basename, dirname, join
#from subprocess import call

#from django.conf import settings
#from django.urls import reverse
#from django.test import TestCase
#from django.test import override_settings
#from unittest.mock import Mock, patch
#from model_bakery.baker import make
#
#from rest_framework.serializers import ValidationError
#from rest_framework.status import HTTP_201_CREATED
## from nose.plugins.attrib import attr

#from ufo.models import InputEvent User

#from ..base import BaseTestCase


#class PostProfileEventSuccessTest(BaseTestCase):
    ## При получении валидного события, оно должно быть сохранено в БД.

    #def setUp(self):
        ## GIVEN User with app_id
        #make(User, app_ids=['123'])

    #def test_post_profile_event_success(self):
        ## WHEN user POSTs valid event data
        #response = self.client.post(reverse('api_event'), data={
            #'app_id': '123', 'timestamp': '2016-12-30T23:59', 'type': 'userprofile'})

        ## THEN response status should be HTTP_201_CREATED
        #self.assertEqual(response.status_code, HTTP_201_CREATED)

        ## AND oneInputEventshould get created
        #self.assertEqualInputEventobjects.count(), 1)
