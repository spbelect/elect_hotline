# -*- coding: utf-8 -*-
import json
import sys
from base64 import urlsafe_b64encode
from binascii import unhexlify
from dataclasses import asdict
from datetime import datetime, timedelta
#from os.path import basename
from urllib.parse import urlencode
from typing import Optional

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
    int16, Answer, AnswerImage, QuizTopic, Question, Region, WebsiteUser, 
    MobileUser, Election, ClientError, Campaign, Organization, Contact
)


class ContactShape(pydantic.BaseModel):
    name: str
    value: str
    #type: Literal['ph', 'vk', 'tg', 'fb', 'wa']
    
    organization_id: str
    campaign_id: Optional[str] = None
    
    
@api_view(['POST'])
def contacts(request):
    contact = ContactShape(**request.data)
    org = get_object_or_404(Organization, id=contact.organization_id)
    if request.user not in org.admins:
        raise drf.PermissionDenied()
    if contact.campaign_id and not org.campaigns.filter(id=contact.campaign_id).exists():
        raise drf.ValidationError('No such campaign')
    #import ipdb; ipdb.sset_trace()
    Contact.objects.create(**contact.model_dump())
    return Response({'status': 'ok'})
    
    
@api_view(['DELETE'])
def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.user not in contact.organization.admins:
        raise drf.PermissionDenied()
    if request.method == 'DELETE':
        contact.delete()
    #else:
        #contact.update(**request.data)
    return Response({'status': 'ok'})


