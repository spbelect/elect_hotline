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
from pydantic import UUID4, BaseModel, field_validator, Field

from ufo import api
from ufo.models import Organization


# def get_form(request, id: Literal['new'] | Annotated[UUID4, Strict(False)]):


@api.html.get('/organizations/{uuid:id}')
def get_form_by_id(request, id: UUID4):
    org = get_object_or_404(Organization, id=id)

    if not org.creator == request.user:
        # Unauthorized
        raise HttpError(401, _("You don't have permission to edit this organization."))

    return render(request, 'views/organizations/id/edit.html', dict(
        org = org
    ))


@api.html.get('/organizations/new')
def get_form(request):
    return render(request, 'views/organizations/id/edit.html')


class OrgSchema(ModelSchema):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'regions']
        fields_optional = ['id']

    name: str = Field(min_length=3)

    # @field_validator('*')
    # def coerce_none(cls, v):
    #     """
    #     Treat regions__id='' in url query as None. So that field does not appear in
    #     resulting queryset.
    #     """
    #     return None if v in ('null', ['null'], [], '') else v


@api.html.post('/organizations/{uuid:id}')
def post_form_by_id(request, id: UUID4, data: Form[OrgSchema]):
    print(data)
    # import ipdb; ipdb.sset_trace()
    org = get_object_or_404(Organization, id=data.id)

    if not org.creator == request.user:
        # Unauthorized
        raise HttpError(401, _("You don't have permission to edit this organization."))

    org.update(name=data.name)
    org.regions.set(data.regions)



@api.html.post('/organizations/new')
def post_form(request, data: Form[OrgSchema]):
    org = Organization.objects.create(
        name=data.name,
        creator=request.user
    )
    org.regions.set(data.regions)

    messages.info(request, _('Organization {name} successfully created.').format(name=org.name))
    # return render(request, 'views/organizations/edit.html')
