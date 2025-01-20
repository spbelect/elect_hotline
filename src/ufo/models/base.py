# -*- coding: utf-8 -*-
from hashlib import md5

from django.db.models import Model
from django.db.models import ForeignKey, SET_NULL
from django.utils import timezone


def update(self, **kwargs):
    """
    Use this method to update and save model instance in single call:

    >> class User(Model):
    ..     update = base.update
    >>
    >> user.update(email='user@example.com', last_name='Bob')

    is a shortcut for

    >> user.email = 'user@example.com'
    >> user.last_name = 'Bob'
    >> user.save(update_fields=['email', 'last_name'])

    """
    for attr, val in kwargs.items():
        setattr(self, attr, val)

    #self.__class__.objects.filter(pk=self.pk).update(**kwargs)
    self.save(update_fields=kwargs)


def FK(*args, **kw):
    return ForeignKey(*args, **dict(dict(on_delete=SET_NULL, null=True, blank=True), **kw))


def int16(string):
    if string is None:
        return None
    return int(md5(string.encode('utf8')).hexdigest(), 16) % 32767  # 2**16 / 2 
