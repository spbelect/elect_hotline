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
#from rest_framework.status import HTTP_200_OK
## from nose.plugins.attrib import attr

#from ufo.models import InputEvent User


##class GetEventsTest(TestCase):
    ### Неавторизованным ползователям должно быть запрещено получать запросе список событий.

    ##def setUp(self):
        ### GIVEN User with app_id
        ##make(User, app_ids=['123'])
        ##makeInputEvent data={'app_id': '123'})

    ##def test_post_event(self):
        ### WHEN user POSTs valid event data
        ##response = self.client.get(reverse('api_event'))

        ### THEN response status should be HTTP_200_OK
        ##self.assertEqual(response.status_code, HTTP_200_OK)

        ### AND oneInputEventshould get created
        ###self.assertEqualInputEventobjects.count(), 1)
