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

#from ufo.models import Region, User, appform, AppFormInput, AppFormInputs
#from ..base import BaseTestCase


#class GetGeneralappformsSuccessTest(BaseTestCase):
    ## При запросе блокформ должен возвращаться JSON список

    #def setUp(self):
        ## GIVEN User with app_id
        ##make(User, app_ids=['123'])

        ## GIVEN general appform
        #bf = make(appform, id='a2', name='anketa2', form_type='GENERAL', order=2)

        ## AND another one
        #bf = make(appform, id='a1', name='anketa1', form_type='GENERAL', order=1)
        ## AND 3 multibool inputs
        #make(AppFormInputs, input__id='3', appform=bf, input__input_type='MULTI_BOOL', order=3)
        #make(AppFormInputs, input__id='2', appform=bf, input__input_type='MULTI_BOOL', order=2)
        #make(AppFormInputs, input__id='1', appform=bf, input__input_type='MULTI_BOOL', order=1)


    #def test_get_general_appforms_success(self):
        ## WHEN user GETs regions list
        #response = self.client.get(reverse('api_appform_general'))

        ## THEN response status should be HTTP_200_OK
        #self.assertEqual(response.status_code, HTTP_200_OK)

        ## AND forms and inputs should be returned, sorted by order
        #assert response.data == [
        #OrderedDict(
            #inputs=[
                #OrderedDict(
                    #input_id='1',
                    #input_type='MULTI_BOOL',
                    #label=ANY,
                    #help_text=None,
                    #extra_tag=None,
                    #alarm_bool=None),
                #OrderedDict(
                    #input_id='2',
                    #input_type='MULTI_BOOL',
                    #label=ANY,
                    #help_text=None,
                    #extra_tag=None,
                    #alarm_bool=None),
                #OrderedDict(
                    #input_id='3',
                    #input_type='MULTI_BOOL',
                    #label=ANY,
                    #help_text=None,
                    #extra_tag=None,
                    #alarm_bool=None),
            #],
            #form_id='a1',
            #name='anketa1',
            #form_type='GENERAL',
            #google_form=None,
            #elections=None,
        #),
        #OrderedDict(
            #inputs=[],
            #form_id='a2',
            #name='anketa2',
            #form_type='GENERAL',
            #google_form=None,
            #elections=None,
        #)]
