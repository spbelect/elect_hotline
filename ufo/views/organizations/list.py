from datetime import datetime
from typing import Literal

import django

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from ninja import FilterSchema, Field, Query, Header
from pydantic import UUID4, BaseModel, field_validator

from ufo import api
from ufo.models import Organization


class Filters(FilterSchema):
    regions__id: str | None = None

    @field_validator('*')
    def coerce_none(cls, v):
        """
        Treat regions__id='' in url query as None. So that field does not appear in
        resulting queryset.
        """
        return None if v in ('null', ['null'], [], '') else v


@api.html.get('/organizations')
def get_organizations(request, filters: Query[Filters], page: Header[int] = 1):
    orgs = filters.filter(Organization.objects.prefetch_related('regions'))

    paginator = Paginator(orgs, per_page=1)

    return render(request, 'views/organizations/list.html', dict(
        page = paginator.get_page(page),
        filters = filters
    ))
