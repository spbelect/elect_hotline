from django.conf import settings
from django.db.models import Max, Q
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
#from django.shortcuts import render

from loguru import logger
from ninja import ModelSchema, Query, Form, Schema
from ninja.orm import create_schema
from pendulum import now
from typing_extensions import Literal

from ufo import api

from ufo.models import (
    int16, Answer, AnswerImage, QuizTopic, Question, Region, WebsiteUser, Munokrug,
    MobileUser, Election, ClientError, Campaign, Organization, Contact, Country
)


@api.v4.get(
    '{str:country}/regions/{int:region}/elections/',
    response = list[create_schema(
        Election, fields=['name', 'flags', 'region', 'munokrug', 'date']
    )]
)
async def get_elections(
    request,
    country: Country.ID,
    region: int   # Region id without country prefix
):
    """
    Get elections running from past month to the next month in given region.
    Includes federal, regional, and municipal elections.
    """

    filter = Q(region_id = f'{country}_{region}')  # Regional and municipal
    filter |= Q(region__isnull=True, country=country)  # Federal

    elections = Election.objects.filter(filter,
        date__gt = now().subtract(days=60),  # From previous month
        date__lt = now().add(days=60),  # To next month
    ).order_by('date', 'region')

    return [x async for x in elections]


