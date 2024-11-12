# -*- coding: utf-8 -*-
from base64 import b64encode
from binascii import unhexlify
from datetime import datetime, date, timedelta
from enum import Enum
from operator import __or__ as OR
from functools import reduce
from typing import Optional
from typing import Union

import arrow
import django
import pendulum
from dateutil.parser import parse as dtparse
from django.apps import apps
from django.conf import settings
from django.core import exceptions
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from django.forms import Form, ModelChoiceField
from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.timezone import now
from django_select2.forms import ModelSelect2Widget
#from django.shortcuts import render
from loguru import logger
from pydantic import UUID4
from pydantic.dataclasses import dataclass
from rest_framework.generics import CreateAPIView, ListCreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.exceptions import ValidationError, PermissionDenied
#from rest_framework.views import APIView
from rest_framework.response import Response
from typing_extensions import Literal

from ..models import (
    Answer, Region, WebsiteUser, Munokrug, MobileUser, Election, Campaign, int16, Organization
)

from ufo.apps import UfoConfig


@login_required
def organizations(request):
    #query = HistoryQuery(**request.GET.dict())
    #import ipdb; ipdb.sset_trace()

    return render(request, 'organizations.html', context=dict(

        organizations = Organization.objects.all(),
        #answers = query.answers,
        #queryform = QueryForm(),
    ))
     

def manage_campaigns(request, orgid):
    #query = HistoryQuery(**request.GET.dict())
    #import ipdb; ipdb.sset_trace()
    org = get_object_or_404(Organization, id=orgid)
    if request.user not in org.admins:
        raise django.core.exceptions.PermissionDenied()
    
    if request.method == 'POST':
        if request.POST['election_id'] == 'test':
            election = Election.objects.create(
                name='Тестовые выборы',
                date=pendulum.now().end_of('month').add(days=1).date()
            )
        else:
            election = get_object_or_404(Election, id=request.POST['election_id'])
        org.campaigns.create(election=election)
        return redirect(manage_campaigns, orgid=orgid)
    
    # Покажем только федеральные выборы или в регионах организации
    upcoming_elections = Election.objects.filter(date__gte=now()).filter(
        Q(region__isnull=True) | Q(region__in=org.regions.all())
    )
    upcoming_campaigns = org.campaigns.filter(election__in=upcoming_elections)
    return render(request, 'manage_campaigns.html', context=dict(

        #answers = query.answers,
        organization = org,
        upcoming_campaigns = upcoming_campaigns,
        upcoming_elections = upcoming_elections.exclude(campaigns__in=upcoming_campaigns)
    ))
     

def manage_staff(request, orgid):
    #import ipdb; ipdb.sset_trace()
    org = get_object_or_404(Organization, id=orgid)
    if request.user not in org.admins:
        raise django.core.exceptions.PermissionDenied()
    return render(request, 'manage_staff.html', context=dict(

        organization = org,
    ))
     

def manage_tik_emails(request, orgid):
    #import ipdb; ipdb.sset_trace()
    org = get_object_or_404(Organization, id=orgid)
    if request.user not in org.admins:
        raise django.core.exceptions.PermissionDenied()
    return render(request, 'manage_staff.html', context=dict(

        #queryform = QueryForm(),
    ))
     
