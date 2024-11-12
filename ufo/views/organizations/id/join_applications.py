from datetime import datetime
from typing import Literal

import django

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from ninja import ModelSchema, Query, Form, Schema
from ninja.errors import HttpError
from pydantic import UUID4, BaseModel, field_validator, Field, EmailStr

from ufo import api
from ufo.models import Organization


# def get_form(request, id: Literal['new'] | Annotated[UUID4, Strict(False)]):


@api.html.post('/organizations/{uuid:id}/join-applications')
def post_join_application(request, id: UUID4):
    org = get_object_or_404(Organization, id=id)

    if not org.members.filter(id=request.user.id).exists():
        org.join_requests.get_or_create(user=request.user)

    return HttpResponse("""
        <span id="join-{org.id}" class="badge badge-outline"> {msg} </span>
    """.format(org=org, msg=_('Join request sent')))

