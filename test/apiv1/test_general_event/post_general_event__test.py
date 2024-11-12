## -*- coding: utf-8 -*-

#from os import remove
#from os.path import basename, dirname, join
#from subprocess import call

#from django.conf import settings
#from django.urls import reverse
#from django.test import TestCase
#from django.test import override_settings
#from unittest.mock import Mock, patch, ANY
#from model_bakery.baker import make
#
#from rest_framework.serializers import ValidationError
#from rest_framework.status import HTTP_201_CREATED
## from nose.plugins.attrib import attr

#from ufo.models import InputEvent User, appform, AppFormInput, AppFormInputs, Region

#from ..base import BaseTestCase


#class PostGeneralEventSuccessTest(BaseTestCase):
    ## При получении валидного события, оно должно быть сохранено в БД.

    #def setUp(self):
        ## GIVEN User with app_id
        #make(User, app_ids=['123'])
        ## AND region
        #region = make(Region, external_id=78)
        ## AND general appform
        #bf = make(appform, name='anketa', form_type='GENERAL')
        ## AND one multibool input
        #input = make(AppFormInput, id='vbros', label='вброс', input_type='MULTI_BOOL', alarm_bool=True)
        #make(AppFormInputs, input=input, appform=bf)

    #def test_post_general_event_success(self):
        ## WHEN user POSTs valid event data
        #response = self.client.post(reverse('api_event'), format='json', data={
            #'app_id': '123',
            #'timestamp': '2016-12-30T23:59',
            #'type': 'input_event',
            #'input_id': 'vbros',
            #'value': True,
            #'uik': 803,
            #'region_id': '78'})

        ## THEN response status should be HTTP_201_CREATED
        #self.assertEqual(response.status_code, HTTP_201_CREATED)

        ## AND oneInputEventshould get created
        #assert listInputEventobjects.values()) == [{
            #'created': ANY,
            #'data': {
                #'alarm': True,
                #'app_id': '123',
                #'input_id': 'vbros',
                #'region_id': '78',
                #'timestamp': '2016-12-30T23:59',
                #'type': 'input_event',
                #'uik': 803,
                #'value': True},
            #'deleted': False,
            #'id': ANY,
            #'modified': ANY,
            #'timestamp': ANY,
            #'user_id': None,
            #'userprofile_id': 1
        #}]
