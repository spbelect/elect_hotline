# -*- coding: utf-8 -*-
from uuid import uuid4
import json

from django.db.models import (
    Model, ForeignKey, DateField, BooleanField, PositiveSmallIntegerField, TextField,
    CharField, SET_NULL, CASCADE, IntegerField, DateTimeField, EmailField
)
from django.utils.timezone import now

from . import base 




class Tik(Model):
    update = base.update
    id = CharField(max_length=40, default=uuid4, primary_key=True)
    time_created = DateTimeField(default=now, verbose_name='Время создания записи в БД на сервере')
    
    region = ForeignKey('Region', on_delete=SET_NULL, related_name='tiks', null=True, blank=True)
    district = ForeignKey('District', on_delete=SET_NULL, related_name='tiks', null=True, blank=True)
    name = TextField()
    email = TextField(null=True, blank=True)
    phone = TextField(null=True, blank=True)
    address = TextField(null=True, blank=True)
    
    # Seriazlised JSON list of lists
    # Пример: [[0, 99],] или [[400, 449], [2100, 2105]]
    uik_ranges = TextField()
    
    def __str__(self):
        return f'RU{self.region.external_id} ТИК {self.name}'

    @staticmethod
    def find(region, uik):
        """ Найти ТИК по номеру УИК """
        for tik in Tik.objects.filter(region=region, uik_ranges__isnull=False):
            for first, last in json.loads(tik.uik_ranges):
                if first <= int(uik) <= last:
                    return tik
        return None


class TikSubscription(Model):
    """
    Email подписка на жалобы в тик.
    """
    organization = ForeignKey('Organization', related_name='tik_subscriptions', on_delete=CASCADE)
    tik = ForeignKey('Tik', related_name='subscriptions', on_delete=CASCADE)
    email = EmailField()
    creator = ForeignKey('WebsiteUser', on_delete=CASCADE)
    time_created = DateTimeField(default=now, verbose_name='Время создания записи в БД на сервере')
    unsubscribed = BooleanField(default=False)
    
    class Meta():
        ordering = ['organization', 'tik__name']
    
