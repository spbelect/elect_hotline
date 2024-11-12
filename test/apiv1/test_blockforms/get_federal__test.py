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


#class GetFederalappformsSuccessTest(BaseTestCase):
    ## При запросе блокформ должен возвращаться JSON список

    #def setUp(self):
        ## GIVEN User with app_id
        ##make(User, app_ids=['123'])

        ### GIVEN old federal elections
        ##make(Elections, date='2016-11-11')
        ##make(Elections, date='2016-09-11')
        ##make(Elections, date='2015-11-11')

        ## AND federal protocol appform for old elections
        #make(appform, elections__date='2016-11-11', name='protocol', form_type='FEDERAL')
        ## AND federal protocol appform for 2 months older elections
        #make(appform, elections__date='2016-09-11', name='old protocol', form_type='FEDERAL')
        ## AND federal protocol appform for 1 year older elections
        #make(appform, elections__date='2015-11-11', name='oldest protocol', form_type='FEDERAL')



    #def test_get_federal_appforms_success(self):
        ## WHEN user GETs regions list
        #response = self.client.get(reverse('api_appform_federal'))

        ## THEN response status should be HTTP_200_OK
        #self.assertEqual(response.status_code, HTTP_200_OK)

        ## AND forms and inputs should be returned, sorted by order
        #assert response.data == [
        #OrderedDict(
            #inputs=[],
            #form_id=ANY,
            #name='protocol',
            #form_type='FEDERAL',
            #google_form=None,
            #elections=ANY,
        #),
        #OrderedDict(
            #inputs=[],
            #form_id=ANY,
            #name='old protocol',
            #form_type='FEDERAL',
            #google_form=None,
            #elections=ANY,
        #)]
