# -*- coding: utf-8 -*-
from base64 import b64encode
from binascii import unhexlify
from datetime import datetime, timedelta
from enum import Enum
from operator import __or__ as OR
from functools import reduce
from itertools import chain
from typing import Optional

import arrow
import pendulum
import pydantic
from dateutil.parser import parse as dtparse
from django.conf import settings
from django.contrib import messages
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

from ..models import (
    Answer, Region, WebsiteUser, Munokrug, MobileUser, Election, Campaign, int16,
    OrgBranch
)



class AnswersQuery(pydantic.BaseModel):
    """ 
    Фильтр передаваемый в GET запросе.
    """
    # Время уже показанных ответов. Будет сдвинуто вниз на час.
    shown_floor: Optional[datetime] = None
    
    # Показывать только заданные в кампании диапазоны УИК.
    restrict_uik_ranges: Optional[Literal['yes', 'no']] = 'yes'
    
    region: Optional[str] = None
    uik: Optional[int] = None
    #munokrug: Optional[UUID4] = None
    complaint: Optional[Literal['yes', 'no', 'any']] = None
    priority: Optional[Literal['urgent', 'incident', 'any']] = None
    
    
#def merge_ranges(ranges):
    
            
def answers_feed(request):
    return _answers(request, template='answers_feed.html')


def more_answers(request):
    """
    При нажатии пользователем кнопки "Еще" под списком показанных ответов, возвращает 
    ответы поданные раньше времени GET['shown_floor'], в интервале одного часа.
    """
    return _answers(request, template='_feed.html')
    
    
def _answers(request, template):
    query = AnswersQuery(**request.GET.dict())
    
    shown_uik_ranges = []
    filter = Q()
    
    if request.user.is_authenticated:
        # Кампании которые прошли недавно или пройдут в будущем.
        actual_campaigns = Campaign.objects.filter(
            organization__members = request.user,
            election__date__gt = now() - timedelta(days=10),
        )
        if query.region:
            actual_campaigns = actual_campaigns.filter(election__region=query.region)
            
            if query.restrict_uik_ranges == 'yes' and not query.uik:
                # Запрошена региональная лента, с ограничением диапазонов УИК.
                
                orgbranches = OrgBranch.objects.filter(
                    organization__members = request.user,
                    region = query.region
                )
                if orgbranches and all(x.uik_ranges for x in orgbranches):
                    # Все организации этом регионе имеют ограниченные диапазоны УИКов.
                    # Покажем только эти диапазоны и кнопку "показать все".
                    shown_uik_ranges = chain(*(x.get_uik_ranges() for x in orgbranches))
                    uik_filter = Q()
                    for branch in orgbranches:
                        for first, last in branch.uik_ranges:
                            uik_filter |= Q(uik__gte=first, uik__lte=last)
                    filter &= uik_filter
                    
        logger.debug(f'{actual_campaigns}')
        
        if actual_campaigns:
            last_election = actual_campaigns.last().election
        
            if now().date() >= last_election.date:
                # После наступления дня голосования покажем ответы данные в течение 10 дней.
                # (Скроем ответы которые были даны до дня голосования, считаем тестовыми)
                # TODO: мб показать только c 8 утра?
                filter &= Q(
                    timestamp__gte = last_election.date,
                    timestamp__lte = last_election.date + timedelta(days=10)
                )
    
    if query.region:
        filter &= Q(region=query.region)
    if query.uik:
        filter &= Q(uik=query.uik)
    #elif query.munokrug:
        #munokrug = get_object_or_404(Munokrug, pk=query.munokrug)
        #uik_filter = Q()
        #for first, last in json.loads(munokrug.uik_ranges):
            #uik_filter |= Q(uik__gte=first, uik__lte=last)
        #filter &= Q(region=munokrug.region) & uik_filter
        
    if query.complaint == 'no':
        filter &= Q(uik_complaint_status=int16('не подавалась'))
    elif query.complaint == 'yes':
        filter &= ~Q(uik_complaint_status=int16('не подавалась'))
        #filter &= Q(uik_complaint_status__isnull=False)
    
    if query.priority == 'incident':
        filter &= Q(is_incident=True, revoked=False)
    elif query.priority == 'urgent':
        filter &= Q(is_incident=True, revoked=False)  # TODO
        
    if query.shown_floor:
        # Answers which was submitted earlier than currently shown answers.
        filter &= Q(timestamp__lt=query.shown_floor)

    logger.debug(f'{filter}')
    
    answers = Answer.objects.filter(filter)
    
    if answers.exists():
        # Round floor down to the start of hour when next answer was submitted.
        floor = answers.first().timestamp.astimezone(request.user.tz)
        floor = pendulum.instance(floor).start_of('hour')
    else:
        floor = pendulum.now().start_of('hour')
        
    logger.debug(f'{floor} {answers.count()}')
    
        
    return render(request, template, dict(
        region = Region.objects.get(id=query.region) if query.region else None,
        uik = query.uik,
        shown_uik_ranges = shown_uik_ranges,
        
        # Число ответов за все время последней кампании в запрошенном регионе/мунокруге или уике.
        num_answers = answers.count(),  
        
        # Ответы данные с начала до конца одно-часового интервала.
        answers = answers.filter(
            timestamp__gte=floor, 
            timestamp__lte=floor.end_of('hour')
        ),
        floor = floor,                 # Начало временного интервала.
        ceil = floor.end_of('hour'),   # Конец временного интервала.
        

    ))

