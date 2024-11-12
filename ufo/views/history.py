from datetime import datetime, date, time, timezone, timedelta
from typing import Literal, Any, Optional
from collections.abc import Iterator
import csv

import django

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from ninja import FilterSchema, Field, Query, Header
from ninja.errors import HttpError
from pendulum import now
from pydantic import UUID4, BaseModel, field_validator, computed_field
from pydantic import conint, conlist, constr, Json

from ufo import api
from ufo.models import Answer, int16
import utils


class Exclude(list):
    """
    A list which is always True, even if empty.
    Tricks ninja.FilterSchema to skip pydantic field from generating queryset.
    """
    def __bool__(self):
        return True


# class TimeFilters(FilterSchema):

class Filters(FilterSchema):
    """
    >>> Filters(date__gt='2018-11-13', time__gt='08:00').get_filter_expression()
    <Q: (AND: )>
    """

    date__gt: date | Literal["null", ""] | None = Field(None, q=Exclude())
    time__gt: time | Literal["null", ""] | None = Field(time(0,0), q=Exclude())

    date__lt: date | Literal["null", ""] | None = Field(None, q=Exclude())
    time__lt: time | Literal["null", ""] | None = Field(time(0,0), q=Exclude())

    def __call__(self, request):
        q = self._connect_fields()

        if self.date__gt and self.time__gt:
            dt = datetime.combine(self.date__gt, self.time__gt)
            q &= Q(timestamp__gt=dt.replace(tzinfo=request.user.tz))

        if self.date__lt and self.time__lt:
            dt = datetime.combine(self.date__lt, self.time__lt)
            q &= Q(timestamp__lt=dt.replace(tzinfo=request.user.tz))

        print(q)
        return Answer.objects.filter(q)

    # timestamp__gt: Optional[datetime | Literal[""]] = Field(None, exclude=True)

    # munokrug: Optional[UUID4] = None
    region_id__in: Json[list[str]] | Literal["null"] | None = None
    uik: int | Literal["null", ""] | None = None
    complaint: Literal['yes', 'no', 'any', 'null'] | None = None
    # priority: Optional[Literal['urgent', 'incident', 'any']] = None
    include_revoked: bool = True

    # @property
    # def model_fields(self):
    #     return {}
    #     return {k: v for k, v in super().model_fields if v.exclude is True}

    # @computed_field
    # def timestamp__gt(self) -> datetime:
    #     return datetime.fromisoformat(f'{self.date__gt}T{self.time__gt}')

    def filter_complaint(self, value: Literal['yes', 'no', 'any', 'null']) -> Q:
        if value == 'no':
            return Q(uik_complaint_status=int16('не подавалась'))
        elif value == 'yes':
            return ~Q(uik_complaint_status=int16('не подавалась'))
        return Q()

    def filter_include_revoked(self, value: bool) -> Q:
        if value is False:
            return Q(revoked=False)
        return Q()

    @field_validator('*')
    def coerce_none(cls, v):
        """
        Treat region_id=["null"] in url query as None. So that field does not appear in
        resulting queryset.
        """
        return None if v in ('null', ['null'], [], '') else v


@api.html.get('/history')
def answers_history(request, filters: Query[Filters], page: Header[int] = 1):
    paginator = Paginator(filters(request), per_page=2)
    return render(request, 'views/history.html', dict(
        page = paginator.get_page(page),
        filters = filters
    ))


class DummyStreamWriter():
    def write(self, row: str) -> str:
        """ Called by writer.writerow() """
        return row   # Will be consequently returned by writer.writerow()


@api.html.get('/history/export-csv')
def export_csv(request, filters: Query[Filters]):
    if not request.user.is_active:
        raise HttpError(status=401)  # Unauthorized

    def generate_rows() -> Iterator[str]:
        answers = filters(request).select_related('question', 'appuser')
        writer = csv.writer(DummyStreamWriter())

        yield writer.writerow([
            'Регион',
            'УИК',
            'Время',
            'Фамилия',
            'Имя',
            'Email',
            'Телефон',
            'Роль',
            'id Вопроса',
            'Вопрос',
            'Ответ',
            'Отозван',
        ])
        for answer in answers.iterator(chunk_size=2000):
            authorized = answer.appuser.id in request.user.disclosed_appusers
            yield writer.writerow([
                answer.region_id,
                answer.uik,
                answer.timestamp.strftime('%Y-%m-%d %H:%M'),
                answer.appuser.first_name if authorized else '',
                answer.appuser.last_name if authorized else '',
                answer.appuser.email if authorized else '',
                answer.appuser.phone if authorized else '',
                answer.role,
                answer.question_id,
                answer.question.label,
                answer.get_value(),
                answer.revoked,
            ])

    response = StreamingHttpResponse(
        generate_rows(),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="answers.csv"'
    return response

