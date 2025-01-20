# -*- coding: utf-8 -*-
import json
import sys
from base64 import urlsafe_b64encode
from binascii import unhexlify
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Optional, List
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
from pydantic import conint, conlist, constr, Json
from pydantic.dataclasses import dataclass
from requests import get
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, ListCreateAPIView, ListAPIView, UpdateAPIView
from rest_framework import exceptions as drf
from rest_framework.permissions import IsAuthenticated
#from rest_framework.views import APIView
from rest_framework.response import Response
from ska import sign_url
from typing_extensions import Literal
import boto3
import pendulum
import pydantic 
import sentry_sdk

import ufo
from ufo.models import (
    int16, Answer, AnswerImage, QuizTopic, Question, Region, WebsiteUser, Munokrug, 
    MobileUser, Election, ClientError, Campaign, Organization, TikSubscription, OrgBranch,
    OrgMembership
)


class OrgShape(pydantic.BaseModel):
    name: constr(min_length=2, max_length=100, strip_whitespace=True)
    regions: conlist(str, min_length=1, max_length=4)
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def organizations(request):
    data = OrgShape(**request.data)
    if request.user.owned_orgs.exists():
        return Response(status=400, data={
            'status': 'validation error',
            'errors': 'Вы не можете создать больше одной организации'
        })
    
    org = Organization.objects.create(creator=request.user, name=data.name)
    org.regions.set(data.regions)
    return Response({'status': 'ok'})
    

@api_view(['DELETE', 'PATCH'])
def org_edit(request, orgid):
    org = get_object_or_404(Organization, id=orgid)
    if not request.user == org.creator:
        raise drf.PermissionDenied()
    
    if request.method == 'DELETE':
        org.delete()
    else:
        data = OrgShape(**request.data)
        org.update(name=data.name)
        for region in data.regions:
            org.branches.get_or_create(region_id=region)
        for region in org.regions.all():
            if region.id not in data.regions:
                org.regions.remove(region)
    return Response({'status': 'ok'})
    
    
Range = conlist(conint(gt=0, lt=9999), min_length=2, max_length=2)

class BranchShape(pydantic.BaseModel):
    uik_ranges: Json[conlist(Range, max_length=10)]

    
@api_view(['DELETE', 'PATCH'])
def org_branch_edit(request, id):
    branch = get_object_or_404(OrgBranch, id=id)
    if not request.user == branch.organization.creator:
        raise drf.PermissionDenied()
    if request.method == 'DELETE':
        branch.delete()
    else:
        data = BranchShape(**request.data)
        branch.update(**data.model_dump())
    return Response({'status': 'ok'})

    
@api_view(['POST'])
def org_members(request, orgid):
    org = get_object_or_404(Organization, id=orgid)
    if request.user not in org.admins:
        raise drf.PermissionDenied()
    
    if org.members.filter(email=request.data['email']).exists():
        return Response(status=400, data={
            'status': 'validation error', 
            'errors': 'Пользователь уже добавлен'
        })
    
    # validators.validate_email(request.data['email'])
    user, created = WebsiteUser.objects.get_or_create(email=request.data['email'])
    if created:
        org.orgmembership_set.create(user=user, role='invited')

        url = sign_url(
            auth_user=user.email,
            secret_key=settings.SKA_SECRET_KEY,
            url=request.build_absolute_uri(f'/auth/login/')
        )

        subject = f'[uik.info] Приглашение от {org.name}'
        body = (
            f'{request.user} приглашает вас присоединиться к организации {org.name} '
            f'для наблюдения за выборами на сайте uik.info.\n\n'
            f'Чтобы принять приглашение перейдите по ссылке: {url}'
        )
    else:
        # Пользователь существует. Добавим его как оператора.
        org.orgmembership_set.create(user=user, role='operator')
        org.join_requests.filter(user=user).delete()
        
        subject = f'[uik.info] Вы были добавлены в организацию {org.name}'
        body = (
            f'{request.user} добавил вас в организацию {org.name} '
            f'для наблюдения за выборами на сайте uik.info.'
        )
        
    email = EmailMessage(
        subject = subject,
        body = body,
        from_email = f'"uik.info" <{settings.DEFAULT_FROM_EMAIL}>',
        to = [user.email]
    )
    email.send()
    return Response({'status': 'ok', 'message': 'Приглашение отправлено на электронную почту'})
    
    
class MemberShape(pydantic.BaseModel):
    role: Literal['admin', 'operator']

@api_view(['DELETE', 'PATCH'])
def org_member_edit(request, orgid, userid):
    membership = get_object_or_404(OrgMembership, organization=orgid, user=userid)
    if not request.user == membership.organization.creator:
        raise drf.PermissionDenied()
    if request.method == 'DELETE':
        membership.delete()
    else:
        data = MemberShape(**request.data)
        membership.update(**data.model_dump())
    return Response({'status': 'ok'})


@api_view(['POST'])
def org_join_applications(request, orgid):
    org = get_object_or_404(Organization, id=orgid)
    if request.user in org.members.all():
         return Response(status=400, data={
            'status': 'validation error', 
            'errors': 'Вы уже уже добавлены'
        })
    org.join_requests.get_or_create(user=request.user)
    return Response({'status': 'OK'})
    

@api_view(['DELETE'])
def org_join_application_edit(request, orgid, userid):
    application = get_object_or_404(OrgJoinApplications, organization=orgid, user=userid)
    if request.user not in org.admins:
        raise drf.PermissionDenied()
    
    if request.method == 'DELETE':
        application.delete()
    #else:
        #data = MemberShape(**request.data)
        #membership.update(**data.dict())
    return Response({'status': 'ok'})

