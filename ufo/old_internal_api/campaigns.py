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
from pydantic import conint, conlist
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
    int16, Answer, AnswerImage, QuizTopic, Question, Region, WebsiteUser, Munokrug, 
    MobileUser, Election, ClientError, Campaign, Organization, TikSubscription
)


class CampaignShape(pydantic.BaseModel):
    org: str
    election: Optional[str] = None
    #regions: List[str]
    #type: Literal['ph', 'vk', 'tg', 'fb', 'wa']
    
    #organization_id: str
    #campaign_id: Optional[str] = None
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def campaigns(request):
    #import ipdb; ipdb.sset_trace()
    #election = request.data.election()
    data = CampaignShape(**request.data)
    org = get_object_or_404(Organization, id=data.org)
    if request.user not in org.admins:
        raise drf.PermissionDenied()
    
    logger.debug(request.data)
    if data.election:
        org.campaigns.create(election_id=data.election)
    else:
        org.campaigns.create(election=Election.objects.get_or_create(
            name='Тестовые выборы',
            date=pendulum.now().end_of('month').add(days=1).date()
        )[0])
    return Response({'status': 'ok'})
    
    

@api_view(['DELETE', 'PATCH'])
def campaign_edit(request, pk):
    camp = get_object_or_404(Campaign, pk=pk)
    if not request.user in camp.organization.admins:
        raise drf.PermissionDenied()
    if request.method == 'DELETE':
        camp.delete()
    else:
        raise NotImplementedError()
        #data = CampaignPatch(**request.data)
        #camp.update(uik_ranges=data.uik_ranges)
    return Response({'status': 'ok'})
