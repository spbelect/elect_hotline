# -*- coding: utf-8 -*-
import json
import sys
from base64 import urlsafe_b64encode
from binascii import unhexlify
from dataclasses import asdict
from datetime import datetime, timedelta
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
from requests import get
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, ListCreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
#from rest_framework.views import APIView
from rest_framework.response import Response
from ska import sign_url
from typing_extensions import Literal
import boto3
import pendulum
import pydantic 
import sentry_sdk

from ufo.models import (
    int16, Answer, AnswerImage, QuizTopic, Question, Region, WebsiteUser, Munokrug, 
    MobileUser, Election, ClientError, Campaign, Organization, TikSubscription, Tik
)
import ufo


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_tik_email(request, id):
    answer = get_object_or_404(Answer, id=id)
    
    try:
        recipients = send_tik_complaint(answer)
    except validators.ValidationError as e:
        sentry_sdk.capture_exception(e)
        return Response({'status': str(e)}, status=400)
    
    return Response({'status': 'OK', 'recipients': recipients})
    

def send_tik_complaint(answer):
    try:
        validators.validate_email(answer.appuser.email)
    except validators.ValidationError as e:
        sentry_sdk.capture_exception(e)
        return
    
    tik = Tik.find(answer.region, answer.uik)
    if not tik or not tik.email:
        return
    
    #to, bcc = answer.get_email_recipients()
    subscriptions = list(tik.subscriptions.filter(unsubscribed=False).values_list('email', flat=True))
    
    email = EmailMessage(
        subject = f'УИК {answer.uik} Жалоба',
        body = answer.tik_complaint_text,
        from_email = f'"{answer.appuser.last_name} {answer.appuser.first_name}" <{settings.DEFAULT_FROM_EMAIL}>',
        to = [tik.email],
        bcc = subscriptions + [answer.appuser.email],
        reply_to = [answer.appuser.email],
        #headers={'Message-ID': 'foo'},
    )
    for image in answer.images.filter(deleted_by_user=False):
        #url = 'https://s3.eu-central-1.amazonaws.com/ekc-uploads/433b7b0206d0d23306fcaebea1c11840Screenshot_20190112_132357_x.jpg'
        response = get(f'https://s3.eu-central-1.amazonaws.com/ekc-uploads/{image.filename}')
        
        #response = get(url, stream=True)
        #email.attach(basename(url), BytesIO(response.content))
        email.attach(image.filename, response.content)
    email.send()
    #email.to = answer.appuser.email
    #email.bcc = 
    
    answer.update(tik_complaint_status=int16('email отправлен'))
    logger.debug(f'Email sent to {email.to + email.bcc}')
    #return to + bcc


@api_view(['POST'])
def send_login_link(request):
    validators.validate_email(request.data['email'])
    link = sign_url(
        auth_user=request.data['email'],
        secret_key=settings.SKA_SECRET_KEY,
        url=request.build_absolute_uri(f'/auth/login/')
    )
    
    email = EmailMessage(
        subject = f'Вход на uik.info',
        body = f'Ссылка для входа на сайт: {link}',
        from_email = f'"uik.info" <{settings.DEFAULT_FROM_EMAIL}>',
        to = [request.data['email']]
    )
    email.send()
    
    return Response({'status': 'OK', 'message': 'Ссылка отправлена на электронную почту.'})
    
