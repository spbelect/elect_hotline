# -*- coding: utf-8 -*-
import json
import sys
from os.path import basename
from base64 import b64encode
from binascii import unhexlify
from datetime import datetime, timedelta, timezone as tz


import django.core.exceptions
import ninja.errors

from botocore.client import Config
from dateutil.parser import parse as dtparse
from django.core import validators
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models import Max, Q
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render
#from django.shortcuts import render
from loguru import logger
from ninja import ModelSchema, Query, Form, Schema
from pendulum import now
from pydantic import BaseModel, ValidationInfo, field_validator, BeforeValidator, Field, AfterValidator
from typing_extensions import Literal, Annotated

import sentry_sdk

from ufo import api
from ufo.models import (
    int16, Answer, AnswerImage, QuizTopic, Question, Region, WebsiteUser, Munokrug, 
    MobileUser, Election, ClientError, Campaign, Organization, TikSubscription
)



class StatusResponse(Schema):
    status: str


class AnswerPatch(Schema):
    app_id: str
    revoked: bool
    tik_complaint_text: str
    tik_complaint_status: Literal['отправляется модератору'] | None
    uik_complaint_status: str


@api.v4.patch('answers/{str:id}')
def patch_answer(request, id, data: AnswerPatch) -> StatusResponse:
    """
    Update Answer. User can revoke it or add tik/uik complaint.
    """
    answer = Answer.objects.filter(
        id=id, appuser__app_id=data.app_id,
    ).last()

    if not answer:
        logger.error(f'No answer with id {id} and appid {data.app_id}')
        return 404, {'status': 'no such answer'}
    
    answer.revoked = data.revoked
    answer.uik_complaint_status = int16(data.uik_complaint_status)

    if data.tik_complaint_status == 'отправляется модератору':
        answer.tik_complaint_status = int16('ожидает модератора')
        answer.tik_complaint_text = data.tik_complaint_text
        answer.time_tik_email_request_created = now(tz.utc)

    answer.save()
    
    if data.tik_complaint_status == 'отправляется модератору' \
            and not settings.TIK_EMAIL_MODERATION:
        answer.send_tik_complaint()  # Send email immediately.
        
    return 200, {'status': 'ok'}
    
    

class AnswerSchema(ModelSchema):
    class Meta:
        model = Answer
        fields = [
            'id',
            'uik_complaint_status',
            'tik_complaint_text',
            'timestamp',
            'is_incident',  # TODO: recalculate it via question.incident_conditions
            'role',
            'uik',
            'revoked',
        ]

    question_id:  Annotated[str, Question.exists]
    region_id: Annotated[str, Region.exists]
    uik_complaint_status: Annotated[int, BeforeValidator(int16)]

    tik_complaint_status: Annotated[
        Literal['отправляется модератору'] | None, Field(exclude=True)
    ]
    app_id: Annotated[str, Field(exclude=True)]
    value: Annotated[int | bool, Field(exclude=True)]


@api.v4.post('answers/', response={201: StatusResponse})
def post_answer(request, data: AnswerSchema):
    """
    Create new answer.
    """
    answer = Answer(
        appuser = MobileUser.objects.get_or_create(app_id = data.app_id)[0],
        **data.dict()
    )

    if data.tik_complaint_status == 'отправляется модератору':
        answer.tik_complaint_status = int16('ожидает модератора')
        answer.tik_complaint_text = data.tik_complaint_text
        answer.time_tik_email_request_created = now(tz.utc)

    if isinstance(data.value, bool):
        answer.value_bool = data.value
    else:
        answer.value_int = data.value

    try:
        answer.save()
    except django.core.exceptions.ValidationError as err:
        # TODO: when answer with the same id exists, return status 409 "Conflict" instead
        # of 422 "Unprocessable Content"?
        raise ninja.errors.ValidationError(str(err))
    except Exception as err:
        if 'test ' in ' '.join(sys.argv):
            raise err
        sentry_sdk.capture_exception(err)
        logger.error(str(err))
        # TODO: client backoff
        return 500, {'status': 'server error'}

    if data.tik_complaint_status == 'отправляется модератору' and not settings.TIK_EMAIL_MODERATION:
        answer.send_tik_complaint()  # Отправить email сразу.

    elections = list(Election.objects.positional(answer.region, answer.uik).current())
    if elections:
        logger.debug(f'Active elections: {elections}')
        answer.appuser.elections.add(*elections)
    else:
        logger.warning(
            f'Received answer, but no currently active elections'
            f' for region {answer.region}, UIK {answer.uik}'
        )
        
    return 201, {'status': 'ok'}
    

