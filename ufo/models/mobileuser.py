# -*- coding: utf-8 -*-
import re

from django.db.models import (
    Model, ForeignKey, DateField, BooleanField, PositiveSmallIntegerField, TextField,
    IntegerField, CharField, SET_NULL, DateTimeField)
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils.timezone import now

import requests

from . import base 
from .organization import Organization


def get_entries(url):
    return re.sub('\=[^&]+', '', url).split('?')[1].split('&')


class MobileUser(Model):
    """
    """
    #class Meta():
        #verbose_name = 'Пользователь'

    update = base.update
    
    app_id = CharField(max_length=20, unique=True)
    first_name = TextField(null=True, blank=True)
    last_name = TextField(null=True, blank=True)
    middle_name = TextField(null=True, blank=True)
    phone = TextField(null=True, blank=True)
    telegram = TextField(null=True, blank=True)
    email = TextField(null=True, blank=True)
    role = CharField(max_length=30, null=True, blank=True)
    region = ForeignKey('Region', on_delete=SET_NULL, null=True, blank=True)
    uik = IntegerField(null=True, blank=True)
    time_created = DateTimeField(default=now, verbose_name='Время создания записи в БД на сервере')
    time_last_answer = DateTimeField(null=True, blank=True)

    def tg(self):
        tele = self.telegram.strip() if self.telegram else ''
        if tele.startswith('@'):
            return tele[1:]
        return tele
    
    def __str__(self):
        return 'Юзер %s' % (self.app_id)
    
    def disclosed_to_orgs(self):
        return Organization.objects.filter(campaigns__election__in=self.elections.all()).distinct()
