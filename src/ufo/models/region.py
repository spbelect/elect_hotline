# -*- coding: utf-8 -*-
import json

from uuid import uuid4
from datetime import timezone, timedelta
from typing import Literal

from django.conf import settings
from django.core import checks
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import (
    Model, ForeignKey, DateField, BooleanField, PositiveSmallIntegerField, TextField,
    CharField, SET_NULL, CASCADE, IntegerField, DateTimeField, SmallIntegerField
)
from django.utils.timezone import now

from . import base 


class Region(base.Model):
    """
    """
    class Meta():
        ordering = ['id']
        
    id = CharField(max_length=10, primary_key=True)
    time_created = DateTimeField(default=now, verbose_name='Время создания записи в БД на сервере')
    name = TextField()
    external_id = IntegerField(null=True, blank=True)
    utc_offset = SmallIntegerField(validators=[
        MinValueValidator(-23), MaxValueValidator(23)
    ])
    country = ForeignKey('Country', related_name='regions', on_delete=CASCADE)

    @property
    def tz(self):
        return timezone(timedelta(hours=self.utc_offset))
        
    def __str__(self):
        return '%s %s' % (self.id, self.name)


    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs) or []

        try:
            count = Region.objects.count()
        except Exception as err:
            errors.append(checks.Error(
                f'Не удалось получить количество регионов\n {err}',
                id='ufo.Region.E001',
                hint='Возможно требуется запустить ./manage.py migrate --skip-checks',
                obj=Region
            ))
        else:
            if count == 0:
                errors.append(checks.Warning(
                    f'Не найдено ни одного региона',
                    hint="Запустите ./scripts/regions.py populatedb",
                    id='ufo.Region.W001',
                    obj=Region
                ))

        return errors


with open(settings.SRC_DIR('countries.json')) as data:
    countries = {x['code'].lower(): x for x in json.load(data)}


class Country(Model):
    ID = Literal['ru', 'ua', 'bg', 'kz']

    id = CharField(max_length=10, primary_key=True)
    name = TextField()

    @property
    def flag(self):
        return countries[self.id]['emoji']


    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs) or []

        try:
            count = Country.objects.count()
        except Exception as err:
            errors.append(checks.Error(
                f'Не удалось получить количество стран\n {err}',
                id='ufo.Country.E001',
                hint='Возможно требуется запустить ./manage.py migrate --skip-checks',
                obj=Country
            ))
        else:
            if count == 0:
                errors.append(checks.Error(
                    f'Не найдено ни одной страны',
                    hint="Запустите ./scripts/regions.py populatedb",
                    id='ufo.Country.E002',
                    obj=Country
                ))

            if not Country.objects.filter(id='ru').exists():
                errors.append(checks.Error(
                    f'Не найдено страны с id="ru"',
                    hint="Запустите ./scripts/regions.py populatedb",
                    id='ufo.Country.E003',
                    obj=Country
                ))

        return errors
