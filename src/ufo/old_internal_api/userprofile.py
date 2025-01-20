# -*- coding: utf-8 -*-
import json
import sys
from base64 import urlsafe_b64encode
from binascii import unhexlify
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Optional, List
#from os.path import basename
from urllib.parse import urlencode

from botocore.client import Config
from dateutil.parser import parse as dtparse
from django.core import validators 
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models import Max, Q
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.timezone import now
#from django.shortcuts import render
from loguru import logger
from pydantic.dataclasses import dataclass
from pydantic import conint
from requests import get
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, ListCreateAPIView, ListAPIView, UpdateAPIView
from rest_framework import exceptions as drf
from rest_framework.permissions import IsAuthenticated
#from rest_framework.views import APIView
from rest_framework.response import Response
from typing_extensions import Literal
import boto3
import pendulum
import pydantic 
import sentry_sdk

from ufo.models import (
    int16, Answer, AnswerImage, QuizTopic, Question, Region, WebsiteUser, Munokrug, 
    MobileUser, Election, ClientError, Campaign, Organization, TikSubscription
)


class SettingsShape(pydantic.BaseModel):
    utc_offset: conint(gt=-23, lt=23)
    #country: str
    
    
@api_view(['POST'])
def settings(request):
    data = SettingsShape(**request.data)
    if request.user.is_authenticated:
        request.user.update(utc_offset=data.utc_offset)
        
    request.session['utc_offset'] = data.utc_offset
    
    return Response({'status': 'ok'})
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def wipe_notifications(request):
    request.user.update(unread_notifications=[])
    return Response({'status': 'ok'})
    
    
#@api_view(['DELETE', 'PATCH'])
#def organization_edit(request, id):
    #org = get_object_or_404(Organization, id=id)
    #if not request.user == org.creator:
        #raise drf.PermissionDenied()
    #if request.method == 'DELETE':
        #org.delete()
    #else:
        #org.update(**OrgShape(**request.data).dict())
    #return Response({'status': 'ok'})

