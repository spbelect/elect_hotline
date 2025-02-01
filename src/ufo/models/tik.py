# -*- coding: utf-8 -*-
from uuid import uuid4
import json

from django.db.models import (
    Model, ForeignKey, DateField, BooleanField, PositiveSmallIntegerField, TextField,
    CharField, SET_NULL, CASCADE, IntegerField, DateTimeField, EmailField
)
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_pydantic_field import SchemaField

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
    
    # Example: [[0, 99]] or [[400, 449], [2100, 2105]]
    # TODO: conlist/conint is not supported yet
    # https://github.com/surenkov/django-pydantic-field/issues/72
    uik_ranges: list[list[int]] = SchemaField(
        null=True, blank=True,
        verbose_name=_("Subordinate UIK ranges"),
        help_text=_("List of ranges.")
    )
    
    def __str__(self):
        if self.region:
            return f'TIK {self.region.id} {self.name}'
        else:
            return f'TIK {self.name}'

    @staticmethod
    def find(region, uik):
        """ Найти ТИК по номеру УИК """
        for tik in Tik.objects.filter(region=region, uik_ranges__isnull=False):
            for first, last in tik.uik_ranges:
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
    
