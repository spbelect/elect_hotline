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
##
#from rest_framework.serializers import ValidationError

#from ufo.models import InputEvent User


##@patch('parser.base.StrictRedis', mock_strict_redis_client)


#class PostEventInvalid(TestCase):
    ## При попытке отправки невалидных событий в тестах должна возникать ошибка валидации.
    ## На сервере будет возвращен HTTP_400_BAD_REQUEST

    #def setUp(self):
        ## GIVEN User with app_id
        #make(User, app_ids=['123'])

    #def test_missing_timestamp(self):
        ## WHEN POST without timestamp received
        ## THEN ValidationError raised
        #with self.assertRaisesRegexp(ValidationError, "timestamp.*Обязательное поле."):
            #self.client.post(reverse('api_event'), {'app_id': '123'})
        ## AND noInputEventgets created.
        #self.assertEqualInputEventobjects.count(), 0)

    #def test_missing_app_id(self):
        ## WHEN POST without app_id received
        ## THEN ValidationError raised
        #with self.assertRaisesRegexp(ValidationError, "app_id.*Обязательное поле."):
            #self.client.post(reverse('api_event'), {'timestamp': '123'})
        ## AND noInputEventgets created.
        #self.assertEqualInputEventobjects.count(), 0)

    #def test_invalid_timestamp(self):
        ## WHEN POST with invalid timestamp received
        ## THEN ValidationError raised
        #with self.assertRaisesRegexp(ValidationError, "Datetime has wrong format"):
            #self.client.post(reverse('api_event'), {'app_id': '123', 'timestamp': '123'})
        ## AND noInputEventgets created.
        #self.assertEqualInputEventobjects.count(), 0)
