# -*- coding: utf-8 -*-
from uuid import uuid4

from django.db.models import (
    Model, ForeignKey, DateField, BooleanField, PositiveSmallIntegerField, TextField,
    CharField, SET_NULL, DateTimeField
)
from django.contrib.postgres.fields import ArrayField
from django.utils.timezone import now

from . import base 


class District(Model):
    """
    TODO: Пока не используется
    """
    class Meta():
        verbose_name = 'Район'

    update = base.update
    
    id = CharField(max_length=50, default=uuid4, primary_key=True)
    time_created = DateTimeField(default=now, verbose_name='Время создания записи в БД на сервере')
    uiks = ArrayField(PositiveSmallIntegerField(), null=True, blank=True)
    region = ForeignKey('Region', on_delete=SET_NULL, null=True, blank=True)
    name = TextField()
    telegram_channel = TextField()

    def __str__(self):
        return self.name


class Munokrug(Model):
    """
    Муниципальный округ и ИКМО.
    """
    
    update = base.update
    
    class Meta():
        verbose_name = 'Мун.округ'

    id = CharField(max_length=50, default=uuid4, primary_key=True)
    time_created = DateTimeField(default=now, verbose_name='Время создания записи в БД на сервере')
    region = ForeignKey('Region', on_delete=SET_NULL, null=True, blank=True, related_name='munokruga')
    district = ForeignKey('District', on_delete=SET_NULL, null=True, blank=True)
    name = TextField()
    
    # Seriazlised JSON list of lists
    # Пример: [[0, 99],] или [[400, 449], [2100, 2105]]
    uik_ranges = TextField(default='[]')
    
    ikmo_email = TextField(null=True, blank=True)
    ikmo_phone = TextField(null=True, blank=True)
    ikmo_address = TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    @staticmethod
    def find(region, uik):
        """ Найти мунокруг по номеру УИК """
        for munokrug in Munokrug.objects.filter(region=region, uik_ranges__isnull=False):
            #if int(state.uik) in munokrug.get('uiks', []):
                #return munokrug
            for first, last in json.loads(munokrug.uik_ranges):
                if first <= int(uik) <= last:
                    return munokrug
        return None
        
