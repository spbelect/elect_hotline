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
def get_regions(request, country):
    """
    GET возвращает регионы заданной страны, с названиями, контактами, и диапазонами УИК всех 
    ТИКов и ИКМО каждого региона.
    """
    return Response({region.id: dict(
        id = region.id,
        name = region.name,
        
        # ТИКи
        tiks = [dict(
            id = tik.id,
            email = tik.email,
            phone = tik.phone,
            address = tik.address,
            name = tik.name,
            
            # Пример: [[0, 99],] или [[400, 449], [2100, 2105]]
            uik_ranges = json.loads(tik.uik_ranges or '[]'),
        ) for tik in region.tiks.order_by('name')],
        
        # Мун.округа и ИКМО
        munokruga = [dict(
            id = mo.id,
            name = mo.name,
            ikmo_email = mo.ikmo_email,
            ikmo_phone = mo.ikmo_phone,
            ikmo_address = mo.ikmo_address,
            
            # Пример: [[0, 99],] или [[400, 449], [2100, 2105]]
            uik_ranges = json.loads(mo.uik_ranges or '[]'),
        ) for mo in region.munokruga.order_by('name')],
        
    ) for region in Region.objects.order_by('id')})
    
    
