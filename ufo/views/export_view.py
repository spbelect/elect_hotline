# -*- coding: utf-8 -*-
import csv
from base64 import b64encode
from binascii import unhexlify
from datetime import datetime, date, timedelta
from enum import Enum
from operator import __or__ as OR
from functools import reduce
from typing import Optional

import arrow
import pendulum
from dateutil.parser import parse as dtparse
from django.conf import settings
from django.db.models import Max, Q
from django.forms import Form, ModelChoiceField
from django.http import HttpResponse, Http404
from django.http import StreamingHttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
from django_select2.forms import ModelSelect2Widget
#from django.shortcuts import render
from loguru import logger
from pydantic import UUID4
from pydantic.dataclasses import dataclass
from rest_framework.generics import CreateAPIView, ListCreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.exceptions import ValidationError
#from rest_framework.views import APIView
from rest_framework.response import Response
from typing_extensions import Literal

from ..models import Answer, Region, WebsiteUser, Munokrug, MobileUser, Election, Campaign, int16

from .history_view import HistoryQuery


class Echo(object):
    def write(self, value):
        return value
    

def export_csv(request):
    query = HistoryQuery(**request.GET.dict())
    answers = query.answers.select_related('question', 'appuser')
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    
    def get(appuser, field):
        """ Вернуть значение поля `field` если есть права досутпа, иначе пустую строку. """
        if request.user.is_active and appuser.id in request.user.disclosed_appusers:
            return getattr(appuser, field)
        return ''

    def generate_rows():
        yield writer.writerow([
            'Регион',
            'УИК',
            'Время',
            'Фамилия',
            'Имя',
            'Email',
            'Телефон',
            'Роль',
            'id Вопроса',
            'Вопрос',
            'Ответ',
            'Отозван',
        ])
        for answer in answers.iterator(chunk_size=2000):
            yield writer.writerow([x or '' for x in (
                answer.region_id,
                answer.uik,
                answer.timestamp.strftime('%Y-%m-%d %H:%M'),
                get(answer.appuser, 'first_name'),
                get(answer.appuser, 'last_name'),
                get(answer.appuser, 'email'),
                get(answer.appuser, 'phone'),
                answer.role,
                answer.question_id,
                answer.question.label,
                answer.get_value(),
                answer.revoked,
            )])

    response = StreamingHttpResponse(
        generate_rows(),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="answers.csv"'
    return response

