import asyncio
import json

from datetime import datetime, date, time, timezone, timedelta
from typing import Literal, Any, Optional, Annotated, AsyncGenerator
from collections.abc import Iterator

import django
import sentry_sdk

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, Count
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import gettext as _
from loguru import logger
from ninja import FilterSchema, Query, Header
from ninja.errors import HttpError
from pendulum import now
from pydantic import UUID4, BaseModel, field_validator, computed_field, Field
from pydantic import conint, conlist, constr, Json

from ufo import api
from ufo.models import Answer, int16, Region, WebsiteUser

import ufo.jinja


class Filters(FilterSchema):
    def __call__(self):
        q = self._connect_fields()
        return Answer.objects.filter(q).select_related(
            'region', 'question', 'appuser', 'operator'
        )

    region_id__in: list[str] | Literal["null"] | None = None
    complaint: Literal['yes', 'no', 'any', 'null'] | None = None

    def filter_complaint(self, value: Literal['yes', 'no', 'any', 'null']) -> Q:
        if value == 'no':
            return Q(uik_complaint_status=int16('не подавалась'))
        elif value == 'yes':
            return ~Q(uik_complaint_status=int16('не подавалась'))
        return Q()

    @field_validator('*', mode='before')
    def coerce_null_to_none(cls, value):
        """
        Treat region_id=["null"] in url query as None. So that field does not appear in
        resulting queryset.
        """
        if value in ('null', ['null'], [], ''):
            return None
        return value


@api.html.get('/answers/stream')
async def answers_stream_page(request, filters: Query[Filters]) -> str:
    """
    Answers stream page with filter form. Includes js frontend which connects to
    /answers/stream/sse endpoint.
    """
    return await ufo.jinja.render(request, 'views/answers/stream.html', dict(
        # Show last 3 answers initially.
        answers = [x async for x in filters().order_by('-time_created')[:3]],
        regions = Region.objects.filter(country=request.user.country_id),
        filters = filters,
    ))


@api.html.get('/answers/stream/sse')
async def sse_start(
    request,
    filters: Query[Filters],
    # Frontend will request answers created after the last received answer.
    time_created__gt: datetime
) -> StreamingHttpResponse:
    """
    SSE stream endpoint, which the frontend at views/answers/stream.html connects to.
    Returns text/event-stream streaming HTTP response.
    """
    logger.debug(f'Stream start {time_created__gt=}')

    from . import sse
    return StreamingHttpResponse(
        streaming_content = sse.worker(request, filters, time_created__gt),
        content_type = "text/event-stream",
    )
