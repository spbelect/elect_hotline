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
from rest_framework import exceptions as drf
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


@dataclass
class UploadRequest:
    app_id: str
    content_type: str
    filename: str
    md5: str

@api_view(['POST'])
def upload_slot(request):
    """
    Генерирует AWS S3 presigned POST ссылку клиенту для отправки файла.
    """
    logger.debug(request.data)
    data = UploadRequest(**request.data)  # Validate body
    
    if not data.filename.startswith(data.md5):
        raise drf.ValidationError('Filename should start with md5 hash.')
    
    s3 = boto3.client(
        's3', 
        region_name = "eu-central-1", 
        aws_access_key_id = settings.AWS_ACCESS_KEY,
        aws_secret_access_key = settings.AWS_SECRET_KEY,
        config = Config(signature_version='s3v4')
    )
    
    response = s3.generate_presigned_post(
        'ekc-uploads', data.filename, ExpiresIn=3600,
        Fields = {
            'acl': 'public-read',
            'Content-MD5': b64encode(unhexlify(data.md5)).decode(),
            'Content-Type': data.content_type
        },
        Conditions=[
            {"acl": "public-read"},
            ["starts-with", "$Content-Type", ""],
            ["starts-with", "$Content-MD5", ""]
        ]
    )
    # Клиент сможет отправить файл POST запросом:
    #     requests.post(url, data=fields, files={'file': open(filepath, 'rb')})
    return Response({'url': response['url'], 'fields': response['fields']})


@api_view(['POST'])
def post_image_metadata(request, answerid):
    """
    Клиент отправляет метаданные картинки после того как загрузит файл в AWS S3.
    Эти данные сохраняем в бд как AnswerImage.
    """
    answer = Answer.objects.filter(
        id=answerid, appuser__app_id=request.data['app_id'],
    ).last()
    if not answer:
        logger.error(f'No answer with id {answerid} and appid {request.data["app_id"]}')
        return Response({'status': 'no such answer'}, status=404)
    
    answer.images.create(
        filename = request.data['filename'],
        type = request.data['type'],
        deleted_by_user = request.data['deleted'],
        timestamp = dtparse(request.data['timestamp'])
    )
    return Response({'status': 'ok'})
    
    
@api_view(['PATCH'])
def patch_image_metadata(request, answerid, md5):
    image = get_object_or_404(AnswerImage, answer_id=answerid, md5=md5)
    image.update(
        deleted_by_user = request.data['deleted'],
    )
    return Response({'status': 'ok'})
    
