# -*- coding: utf-8 -*-
import json
import re

from uuid import uuid4
from datetime import datetime, timedelta


from django.db.models import (
    Model, ForeignKey, DateTimeField, NullBooleanField, ManyToManyField, 
    TextField, CharField, PositiveSmallIntegerField, BooleanField, SET_NULL, 
    CASCADE, QuerySet, Q
)
from django.db.models import JSONField
from django.utils.functional import cached_property
from django.utils.timezone import now


from .base import FK
from . import base 
from . import munokrug 


class Contact(Model):
    class Meta():
        ordering = ('value',) 
        
    name = CharField(max_length=200)
    value = CharField(max_length=1000)
    TYPES = [
        ('ph', 'Phone'),
        ('tg', 'Telegram'),
        ('wa', 'WhatsApp'),
        ('vk', 'VK'),
        ('fb', 'Facebook'),
        ('uk', 'Unknown'),
    ]
    type = CharField(max_length=3, choices=TYPES)
    
    organization = FK('Organization', on_delete=CASCADE, related_name='contacts')
    campaign = FK('Campaign', on_delete=CASCADE, related_name='contacts')
    
    @property
    def icon(self):
        return dict({
            'ph': 'phone',
            #'wa': ['https://wa.me/'],
            #'tg': ['https://tg.me/', 'https://telegram.me/'],
            #'vk': ['https://vk.com/'],
            #'fb': ['https://facebook.com/'],
        }).get(self.type, 'globe')
        
    def save(self, *a, **kw):
        if not self.type:
            if re.match('^[\d\s\+\-]+$', self.value):
                self.type = 'ph'
                return super().save(*a, **kw)
            
            links = {
                'wa': ['https://wa.me/'],
                'tg': ['https://tg.me/', 'https://telegram.me/', 'https://t.me/', 'tg://'],
                'vk': ['https://vk.com/'],
                'fb': ['https://facebook.com/']
            }
            for type, patterns in links.items():
                if any(self.value.startswith(x) for x in patterns):
                    self.type = type
                    break
            else:
                self.type = 'uk'
        super().save(*a, **kw)
    
