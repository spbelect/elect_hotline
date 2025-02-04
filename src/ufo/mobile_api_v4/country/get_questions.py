# -*- coding: utf-8 -*-
import json
import sys

from os.path import basename
from base64 import b64encode
from binascii import unhexlify
from datetime import datetime, timedelta

from django.core import validators 
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models import Max, Q
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
#from django.shortcuts import render

from loguru import logger
from ninja import ModelSchema, Query, Form, Schema
from ninja.orm import create_schema
from typing_extensions import Literal

from ufo import api

from ufo.models import (
    int16, Answer, AnswerImage, QuizTopic, Question, Region, WebsiteUser, Munokrug, 
    MobileUser, Election, ClientError, Campaign, Organization, Country
)


class QuizTopicSchema(Schema):
    id: str
    name: str
    questions: list[create_schema(Question, exclude=['time_created'])]


@api.v4.get('{str:country}/questions/', response=list[QuizTopicSchema])
async def get_questions(request, country: Country.ID):
    """
    Get quiz topics with questions.
    """
    # TODO: filter by country
    topics = QuizTopic.objects.filter(country=country).prefetch_related('questions')

    return [x async for x in topics]

