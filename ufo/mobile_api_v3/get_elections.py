# -*- coding: utf-8 -*-
import json
import sys
from os.path import basename
from base64 import b64encode
from binascii import unhexlify
from datetime import datetime, timedelta

from botocore.client import Config
from dateutil.parser import parse as dtparse
from django.core import validators 
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models import Max, Q
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
#from django.shortcuts import render
from loguru import logger
from pydantic.dataclasses import dataclass
from requests import get
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, ListCreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
#from rest_framework.views import APIView
from rest_framework.response import Response
from typing_extensions import Literal
import boto3
import pendulum
import sentry_sdk

from ufo.models import (
    int16, Answer, AnswerImage, QuizTopic, Question, Region, WebsiteUser, Munokrug, 
    MobileUser, Election, ClientError, Campaign, Organization, TikSubscription
)


@api_view(['GET'])
def get_elections(request, region):
    """
    Возвращает ближайшие (предстоящие и прошедшие) выборы в регионе за +-60 дней, вместе с 
    координаторами и их контактами.
    """
    
    elections = Election.objects.filter(
        Q(region_id=region) | Q(region__isnull=True, country=region[:2]),
        date__gt = pendulum.now().subtract(days=60),
        date__lt = pendulum.now().add(days=60),
    ).order_by('date', 'region')
    
    #if not elections:
        #return Response([])
    #campaigns = Campaign.objects.filter(election__in=elections)
    return Response([dict(
        name = elec.name,
        flags = (elec.flags or '').split(','),
        region = elec.region_id,
        date = elec.date,
        coordinators = [{
            'org_id': camp.organization.id,
            'org_name': camp.organization.name,
            'contacts': list(camp.organization.get_contacts().values('name', 'value', 'type')),
            'campaign': {
                'id': camp.id,
                'contacts': list(camp.contacts.values('name', 'value', 'type')),
                'uik_ranges': camp.uik_ranges
            }
        } for camp in elec.campaigns.all()]
    ) for elec in elections])
        
    
