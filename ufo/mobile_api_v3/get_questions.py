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

def _question(q):
    return dict(
        id = q.id,
        label = q.label,
        type = q.type,
        fz67_text = q.fz67_text,
        example_uik_complaint = q.example_uik_complaint,
        
        # Считать ответ на этот вопрос инцидетом если все заданные условия соблюдены.
        # Serialized JSON object, example: { "answer_equal_to": False }
        incident_conditions = q.incident_conditions or {},
        
        # Показывать этот вопрос в анкете если:
        # - текущие выборы имеют заданные флаги (elect_flags)
        # И
        # - даны разрешающие ответы на ограничивающие вопросы (limiting_questions)
        visible_if = {
        
            # Требуемые флаги выборов для показа этого вопроса. Пример: ["dosrochka"]
            'elect_flags': q.elect_flags or [],
            
            # Разрешающие условия на ограничивающие вопросы для показа этого вопроса.
            # Возможные значения:
            # { all: [] } - все условия в списке должны быть соблюдены
            # { any: [] } - хотя бы одно условие в списке соблюдено
            'limiting_questions': q.limiting_questions or {}
        }
    )
        
@api_view(['GET'])
def get_question(request, country, id):
    return Response(_question(get_object_or_404(Question, id=id)))
    
    
@api_view(['GET'])
def get_questions(request, country):
    """
    GET возвращаает все вопросы разделенные по тематическим разделам анкеты.
    """
    return Response([dict(
        id = str(topic.id),
        name = topic.name,
        questions = [_question(q) for q in topic.questions.order_by('topicquestions__sortorder')]
    ) for topic in QuizTopic.objects.all()])
    
