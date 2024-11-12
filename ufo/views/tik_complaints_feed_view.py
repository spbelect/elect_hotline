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
#from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render, redirect
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



@dataclass
class TikComplaintsQuery:
    """ 
    Фильтр передаваемый в GET запросе.
    """
    # Статус запроса отправки письма
    status: Optional[Literal['new', 'sent', 'denied', 'any']] = None  
    
    @property
    def answers(self):
        """
        Usage:
            answers = TikComplaintsQuery(**request.GET.dict()).answers
        """
        filter = Q()
        
        if self.status == 'new':
            filter &= Q(tik_complaint_status=int16('ожидает модератора'), revoked=False)
        elif self.status == 'sent':
            filter &= Q(tik_complaint_status=int16('email отправлен'))
        elif self.status == 'denied':
            filter &= Q(tik_complaint_status=int16('отклонено'))
        else:
            filter &= ~Q(tik_complaint_status=int16('не подавалась'))
        
        return Answer.objects.filter(filter)
        
    
def tik_complaints_feed(request):
    """
    Запросы отправки жалоб по email в тик.
    """
    if not request.user.is_authenticated:
        return redirect('/feed/answers/')
    
    query = TikComplaintsQuery(**request.GET.dict())
    
    user_campaigns = Campaign.objects.filter(organization__members=request.user)
    last_campaign = user_campaigns.last()
    
    if not last_campaign:
        return render(request, 'tik_complaints_feed.html')

    if now().date() < last_campaign.election.date:
        # До дня голосования покажем все ответы данные за 60 дней 
        # до начала голосования.
        answers = query.answers.filter(
            timestamp__gte = last_campaign.election.date - timedelta(days=60)
        )
    else:
        # После наступления дня голосования покажем ответы данные с начала дня голосования
        # в течение 10 дней.
        answers = query.answers.filter(
            timestamp__gte = last_campaign.election.date,
            timestamp__lte = last_campaign.election.date + timedelta(days=10)
        )
    
    actual_campaigns = user_campaigns.filter(election__date=last_campaign.election.date)
    #regions = Region.objects.filter(organizations__members=request.user)

    if None in [x.election.region for x in actual_campaigns]:
        # Актуальна Федеральная кампания. Покажем все регионы организаций в которых юзер состоит.
        regions = Region.objects.filter(organizations__members=request.user)
        location = Q(region__in=regions)
        shown_locations = [x.name for x in regions]
    else:
        # Нет актуальной федеральной кампании. Покажем Email запросы только актуальных 
        # регионов\мунокругов.
        location = Q()
        shown_locations = []
        for campaign in actual_campaigns:
            if campaign.election.munokrug:
                uik_filter = Q()
                for first, last in json.loads(campaign.election.munokrug.uik_ranges):
                    uik_filter |= Q(uik__gte=first, uik__lte=last)
                location |= Q(region=campaign.election.munokrug.region) & uik_filter
                shown_locations.append(campaign.election.munokrug.name)
            else:
                location |= Q(region=campaign.election.region)
                shown_locations.append(campaign.election.region.name)
    answers = answers.filter(location)
    #.filter(
        #time_tik_email_request_created__gt=last_campaign.fromtime,
        #time_tik_email_request_created__lt=last_campaign.totime,
    #)
        
    return render(request, 'tik_complaints_feed.html', dict(

        answers = answers,
        shown_locations = shown_locations,
        #actual_campaigns = actual_campaigns,
    ))

