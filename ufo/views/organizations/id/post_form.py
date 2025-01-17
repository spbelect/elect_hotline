from datetime import datetime
from typing import Literal

import django

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import gettext as _
from loguru import logger
from ninja import ModelSchema, Query, Form, Schema
from ninja.errors import HttpError
from pydantic import UUID4, BaseModel, field_validator, Field

from ufo import api
from ufo.models import Organization


class OrgSchema(ModelSchema):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'regions']
        fields_optional = ['id']

    name: str = Field(min_length=3)


@api.html.post('/organizations/{uuid:id}')
def post_organization(request, id: UUID4, data: Form[OrgSchema]):
    """ Edit existing Organization. """

    org = get_object_or_404(Organization, id=data.id)

    if not org.creator == request.user:
        # Unauthorized
        raise HttpError(401, _("You don't have permission to edit this organization."))

    org.update(name=data.name)
    org.regions.set(data.regions)

    return render(request, 'views/organizations/id/show_form.html', dict(
        org = org
    ))


@api.html.post('/organizations/new')
def post_new_organization(request, data: Form[OrgSchema]):
    """ Create new Organization. """

    org = Organization.objects.create(
        name=data.name,
        creator=request.user
    )
    org.regions.set(data.regions)
    logger.info(f'Created new Organization {org.name} {org.id} by {request.user}')

    # messages.info(request, _('Organization {name} successfully created.').format(name=org.name))

    return redirect(f'/organizations/{org.id}')

