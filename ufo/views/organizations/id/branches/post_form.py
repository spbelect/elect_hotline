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
from ufo.models import OrgBranch


Range = conlist(conint(gt=0, lt=9999), min_length=2, max_length=2)


class BranchSchema(BaseModel):
    uik_ranges: Json[conlist(Range, max_length=10)]


@api.html.post('/organizations/{uuid:orgid}/branches/{str:regionid}')
def post_orgbranch_form(
    request,
    orgid: UUID4,
    regionid: str,
    # TODO: Django-Ninja does not support conslit or Json fields
    # uik_ranges: Form[Json[conlist(Range, max_length=10)]]
):
    branch = get_object_or_404(OrgBranch, organization_id=orgid, region_id=regionid)

    if not branch.organization.creator == request.user:
        # Unauthorized
        raise HttpError(401, _("You don't have permission to edit this organization."))

    data = BranchSchema(**request.POST.dict())
    branch.update(**data.model_dump())
    return redirect(f'/organizations/{branch.organization.id}')

