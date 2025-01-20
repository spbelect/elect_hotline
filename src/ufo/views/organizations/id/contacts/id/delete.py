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



@api.html.delete('/organizations/{uuid:orgid}/contacts/{int:contactid}')
def delete_contact(request, orgid: UUID4, contactid: int):
    org = get_object_or_404(Organization, id=orgid)

    if not org.creator == request.user:
        # Unauthorized
        raise HttpError(401, _("You don't have permission to edit this organization."))

    contact = get_object_or_404(Contact, id=contactid)
    contact.delete()

    return render(request, 'views/organizations/id/contacts/show_form.html', dict(
        org = org
    ))


