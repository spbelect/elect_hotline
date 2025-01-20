# -*- coding: utf-8 -*-
from django.db.models import (
    Model, ForeignKey, DateTimeField, BooleanField, CharField, 
    ManyToManyField, TextField, PositiveSmallIntegerField
)
from django.db.models import JSONField
from django.utils.timezone import now

from . import base 

#


class ClientError(Model):
    """
    Tracebacks received from client apps.
    """

    timestamp = DateTimeField(verbose_name='Когда произошло')
    data = JSONField(verbose_name='Полученный JSON')
    time_created = DateTimeField(default=now, verbose_name='Время создания записи в БД на сервере')

    def __str__(self):
        return 'ClientError-%s' % self.timestamp.isoformat()
