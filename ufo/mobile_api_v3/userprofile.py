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

@api_view(['POST'])
def post_userprofile(request):
    MobileUser.objects.update_or_create(app_id=request.data['app_id'], defaults=dict(
        first_name = request.data['first_name'],
        last_name = request.data['last_name'],
        middle_name = request.data.get('middle_name', None),
        phone = request.data['phone'],
        telegram = request.data['telegram'],
        email = request.data['email'],
    ))
    return Response({'status': 'ok'})
