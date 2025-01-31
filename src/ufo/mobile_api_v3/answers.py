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

import ufo


@api_view(['PATCH'])
def patch_answer(request, answerid):
    answer = Answer.objects.filter(
        id=answerid, appuser__app_id=request.data['app_id'],
    ).last()
    if not answer:
        logger.error(f'No answer with id {answerid} and appid {request.data["app_id"]}')
        return Response({'status': 'no such answer'}, status=404)
    
    tik_complaint_status = request.data['tik_complaint_status']
    #import ipdb; ipdb.sset_trace()
    if tik_complaint_status == 'отправляется модератору':
        extra = {
            'tik_complaint_status': int16('ожидает модератора'),
            'time_tik_email_request_created': now(),
            'tik_complaint_text': request.data['tik_complaint_text'],
        }
    else:
        extra = {}
    print(tik_complaint_status, int16('ожидает модератора'), extra)
        
    answer.update(
        revoked=request.data['revoked'],    
        uik_complaint_status = int16(request.data['uik_complaint_status']),
        **extra
    )
    
    if tik_complaint_status == 'отправляется модератору' and not settings.TIK_EMAIL_MODERATION:
        answer.send_tik_complaint()  # Отправить email сразу.
        
    return Response({'status': 'ok'})
    
    
@api_view(['POST'])
def post_answer(request):
    logger.info(request.data)
    user = MobileUser.objects.get_or_create(app_id = request.data['app_id'])[0]
    question = Question.objects.filter(id=request.data['question_id']).last()
    if not question:
        logger.error(f'No question with id {request.data["question_id"]}')
        return Response({'status': 'no such question'}, status=404)
    
    data = {}
    if isinstance(request.data['value'], bool):
        data['value_bool'] = request.data['value']
    else:
        data['value_int'] = request.data['value']
    
    
    tik_complaint_status = request.data['tik_complaint_status']
    if tik_complaint_status == 'отправляется модератору':
        data.update({
            'tik_complaint_status': int16('ожидает модератора'),
            'time_tik_email_request_created': now(),
            'tik_complaint_text': request.data['tik_complaint_text'],
        })
        
    try:
        answer = Answer.objects.create(
            id = request.data['id'],
            appuser = user,
            question = question,
            uik_complaint_status = int16(request.data['uik_complaint_status']),
            region_id = request.data['region'],
            uik = request.data['uik'],
            role = request.data['role'],
            is_incident = request.data['is_incident'],
            revoked = request.data['revoked'],
            timestamp = dtparse(request.data['timestamp']),
            **data
        )
    except Exception as e:
        if 'test ' in ' '.join(sys.argv):
            raise e
        sentry_sdk.capture_exception(e)
        logger.error(str(e))
    else:
        if tik_complaint_status == 'отправляется модератору' and not settings.TIK_EMAIL_MODERATION:
            answer.send_tik_complaint()  # Отправить email сразу.
    
        elections = list(Election.objects.positional(answer.region, answer.uik).current())
        if elections:
            logger.debug(f'Active elections: {elections}')
            user.elections.add(*elections)
        else:
            logger.warning(f'No active elections for {answer.region}, UIK {answer.uik}')
        
    return Response({'status': 'ok'}, status=201)
    

