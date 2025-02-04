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


class OrgSchema(ModelSchema):
    class Meta:
        model = Organization
        fields = ['id', 'name']

    contacts: list[create_schema(Contact, fields=['name', 'value', 'type'])]


@api.v4.get(
    '{str:country}/regions/{int:region}/organizations/',
    response = list[OrgSchema]
)
async def get_organizations(
    request,
    country: Country.ID,
    region: int  # Region id without country prefix
):
    """
    Get organizations in given region.
    """
    orgs = Organization.objects.filter(
        branches__region=f'{country}_{region}'
    ).prefetch_related('contacts')

    return [x async for x in orgs]


