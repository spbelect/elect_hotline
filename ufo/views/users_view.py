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



def users(request):
    context = {
        'users': MobileUser.objects.all().select_related('region'),
    }
    return render(request, 'users.html', context=dict(
        **context
    ))



