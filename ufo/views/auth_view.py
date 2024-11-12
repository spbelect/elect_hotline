# -*- coding: utf-8 -*-
from base64 import urlsafe_b64encode
from binascii import unhexlify
from datetime import datetime, date, timedelta
from enum import Enum
from hashlib import sha256
from operator import __or__ as OR
from functools import reduce
from typing import Optional
from urllib.parse import urlencode

import django
import arrow
import pendulum
import sentry_sdk

from dateutil.parser import parse as dtparse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
#from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.db.models import Max, Q
from django.forms import Form, ModelChoiceField
from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import now
from django_select2.forms import ModelSelect2Widget
#from django.shortcuts import render
from loguru import logger
from pydantic import UUID4
from pydantic import EmailStr
from pydantic.dataclasses import dataclass
from rest_framework.generics import CreateAPIView, ListCreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.exceptions import ValidationError
#from rest_framework.views import APIView
from rest_framework.response import Response
from ska.contrib.django.ska.decorators import validate_signed_request
from typing_extensions import Literal

import ufo
from ufo.models import (
    Answer, Region, WebsiteUser, Munokrug, MobileUser, Election, Campaign, int16, Organization
)


@validate_signed_request()
def auth_login(request):
    """
    Signed login link handler.
    
    В GET параметрах должна быть валидная подпись
    """
    user = WebsiteUser.objects.get_or_create(email=request.GET['auth_user'])[0]
    
    # if user.last_login and user.last_login > args.time_created \
    #    or now() > args.time_created + timedelta(hours=1):
    #     logger.info('Ссылка устарела')
    #     messages.add_message(request, messages.ERROR, 'Ссылка устарела.')
    #     return redirect('/feed/answers/')
        
    for invitation in user.orgmembership_set.filter(role='invited'):
        invitation.update(role='operator')
        
        # Уведомить создателя оранизации о вступлении нового юзера.
        invitation.organization.creator.unread_notifications.append(
            f'Пользователь {user.email} присоединился к организации {invitation.organization.name}'
        )
        invitation.organization.creator.save()
        
        # Если есть, удалить запрос пользователя на вступление в эту организацию.
        invitation.organization.join_requests.filter(user=user).delete()
        
        
    django.contrib.auth.login(request, user)
    #logger.debug(f'WebsiteUser {user} login ok')
    messages.add_message(request, messages.INFO, f'Вы успешно вошли как {user}.')

    return redirect('/feed/answers/')
    

def auth_logout(request):
    if not request.user.is_authenticated:
        return redirect('/feed/answers/')
    
    django.contrib.auth.logout(request)
    return redirect(request.META.get('HTTP_REFERER') or '/feed/answers/')
