# -*- coding: utf-8 -*-
from base64 import b64encode
from binascii import unhexlify
from datetime import datetime, date, timedelta
from enum import Enum
from operator import __or__ as OR
from functools import reduce
from typing import Optional, Union

import arrow
import pendulum
from dateutil.parser import parse as dtparse
from django.conf import settings
from django.db.models import Max, Q
from django.forms import Form, ModelChoiceField
from django.http import HttpResponse, Http404
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



@dataclass
class HistoryQuery:
    """ 
    Фильтр передаваемый в GET запросе.
    """
    
    show_all: Optional[Literal['yes', 'no']] = None
    
    fromtime: Optional[Union[date, str]] = None
    totime: Optional[Union[date, str]] = None
    #totime: Optional[date] = None
    
    region: Optional[str] = None
    uik: Optional[int] = None
    munokrug: Optional[UUID4] = None
    complaint: Optional[Literal['yes', 'no', 'any']] = None
    priority: Optional[Literal['urgent', 'incident', 'any']] = None
    
    @property
    def answers(self):
        """
        Usage:
            answers = HistoryQuery(**request.GET.dict()).answers
        """
        filter = Q()
        
        if self.region not in (None, 'any', 'null'):
            filter &= Q(region=self.region)
        if self.uik:
            filter &= Q(uik=self.uik)
        elif self.munokrug:
            munokrug = get_object_or_404(Munokrug, pk=self.munokrug)
            uik_filter = Q()
            for first, last in json.loads(munokrug.uik_ranges):
                uik_filter |= Q(uik__gte=first, uik__lte=last)
            filter &= Q(region=munokrug.region) & uik_filter
            
        if self.complaint == 'no':
            filter &= Q(uik_complaint_status=int16('не подавалась'))
        elif self.complaint == 'yes':
            filter &= ~Q(uik_complaint_status=int16('не подавалась'))
            #filter &= Q(uik_complaint_status__isnull=False)
        
        if self.priority == 'incident':
            filter &= Q(is_incident=True, revoked=False)
        elif self.priority == 'urgent':
            filter &= Q(is_incident=True, revoked=False)  # TODO
            
        if self.fromtime:
            filter &= Q(timestamp__gte=self.fromtime)
        if self.totime:
            filter &= Q(timestamp__lte=self.totime)
            
        return Answer.objects.filter(filter)
        

#class QueryForm(Form):
    #region = ModelChoiceField(
        #queryset=Region.objects.all(),
        #label="Регион",
        #empty_label='Регион',
        #widget=ModelSelect2Widget(
            #model=Region,
            #search_fields=['name__icontains'],
        #)
    #)

    #munokrug = ModelChoiceField(
        #queryset=Munokrug.objects.all(),
        #label="Мун. округ",
        #widget=ModelSelect2Widget(
            #model=Munokrug,
            #search_fields=['name__icontains'],
            #dependent_fields={'region': 'region'},
            #max_results=500,
        #)
    #)

def history(request):
    query = HistoryQuery(**request.GET.dict())
    num_total_answers = query.answers.count()
    
    if query.show_all == 'yes':
        answers = query.answers
        displayed_all = True
    else:
        answers = query.answers[:10]
        displayed_all = bool(num_total_answers < 10)
    
    return render(request, 'history.html', context=dict(

        answers = answers,
        num_total_answers = num_total_answers,
        displayed_all = displayed_all
    ))
     
