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
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.utils.timezone import now
#from django.shortcuts import render

from loguru import logger
from typing_extensions import Literal
from typing import Annotated
from ninja import ModelSchema, Query, Form, Schema
from ninja.orm import create_schema
from pydantic import UUID4, BaseModel, Field, Json

from ufo import api

from ufo.models import (
    int16, Answer, AnswerImage, QuizTopic, Question, Region, WebsiteUser, Munokrug, 
    MobileUser, Election, ClientError, Campaign, Organization, TikSubscription, Tik,
    Country
)


class MunokrugSchema(ModelSchema):
    class Meta:
        model = Munokrug
        fields = ['id', 'name', 'uik_ranges', 'ikmo_phone', 'ikmo_email', 'ikmo_address']


class TikSchema(ModelSchema):
    class Meta:
        model = Tik
        fields = ['id', 'name', 'uik_ranges', 'email', 'phone', 'address']

    # TODO: get annotation from django-pydantic-field?
    uik_ranges: list[list[int]] | None


class RegionSchema(Schema):
    id: str
    name: str

    tiks: list[TikSchema]
    munokruga: list[MunokrugSchema]


@api.v4.get('{str:country}/regions/', response=list[RegionSchema])
async def get_regions(request, country: Country.ID):
    """
    Get regions with tiks, municipal districts and corresponding uik ranges.
    """
    regions = Region.objects\
        .filter(country=country)\
        .order_by('id')\
        .prefetch_related('tiks', 'munokruga')

    return [x async for x in regions]



    
