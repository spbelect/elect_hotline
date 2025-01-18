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

from ufo import api
from ufo.models import Organization


@api.html.get('/organizations/{uuid:orgid}/contacts')
def show_orgbranch_form(request, orgid: UUID4):
    org = get_object_or_404(Organization, id=orgid)

    if not org.creator == request.user:
        # Unauthorized
        raise HttpError(401, _("You don't have permission to edit this organization."))

    return render(request, 'views/organizations/id/contacts/show_form.html', dict(
        org = org
    ))

