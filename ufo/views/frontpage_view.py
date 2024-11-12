# -*- coding: utf-8 -*-
from base64 import b64encode
from binascii import unhexlify
from datetime import datetime, timedelta
from enum import Enum
from operator import __or__ as OR
from functools import reduce
from typing import Optional

import arrow
import pendulum
from dateutil.parser import parse as dtparse
from django.conf import settings
from django.db.models import Max, Q
from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
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


#def frontpage(request):
    #is_incident = bool(request.GET.get('is_incident', 'false') == 'true')
    #events = Answer.objects.filter(data__type='input_event').prefetch_related('userprofile')
    #if is_incident:
        #events = events.filter(data__is_incident=True)
    #context = {
        #'events': events.order_by('-timestamp').join(),
    #}
    #return TemplateResponse(request, 'frontpage.html', context=context)

