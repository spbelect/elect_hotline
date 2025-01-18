from datetime import datetime
from typing import Literal

import django

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import gettext as _
from ninja import ModelSchema, Query, Form, Schema
from ninja.errors import HttpError
from pydantic import UUID4, BaseModel, field_validator, Field
from pydantic import conint, conlist, constr, Json

from ufo import api
from ufo.models import Organization, Contact



class ContactSchema(ModelSchema):
    class Meta:
        model = Contact
        fields = ['name', 'value',]
        fields_optional = ['name']


@api.html.post('/organizations/{uuid:orgid}/contacts/new')
def post_new_contact_form(
    request,
    orgid: UUID4,
    data: Form[ContactSchema]
):
    org = get_object_or_404(Organization, id=orgid)

    if not org.creator == request.user:
        # Unauthorized
        raise HttpError(401, _("You don't have permission to edit this organization."))

    Contact.objects.create(organization_id=orgid, **data.dict(exclude_unset=True))

    return render(request, 'views/organizations/id/contacts/show_form.html', dict(
        org = org
    ))


@api.html.post('/organizations/{uuid:orgid}/contacts/{int:contactid}')
def post_existing_contact_form(
    request,
    orgid: UUID4,
    contactid: int,
    data: Form[ContactSchema]
):
    org = get_object_or_404(Organization, id=orgid)

    if not org.creator == request.user:
        # Unauthorized
        raise HttpError(401, _("You don't have permission to edit this organization."))

    contact = get_object_or_404(Contact, id=contactid)
    contact.update(**data.dict(exclude_unset=True))


