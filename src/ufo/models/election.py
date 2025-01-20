# -*- coding: utf-8 -*-
from uuid import uuid4
from datetime import timedelta

from django.db.models import (
    Model, ForeignKey, DateField, BooleanField, PositiveSmallIntegerField, TextField,
    CharField, SET_NULL, CASCADE, DateTimeField, ManyToManyField, QuerySet, Q
)
from django.contrib.postgres.fields import ArrayField
from django.utils.timezone import now

from . import base 


class ElectionQuerySet(QuerySet):
    def positional(self, region, uik):
        from .munokrug import Munokrug
        filter = Q(region__isnull=True)  # federal
        filter |= Q(region=region, munokrug__isnull=True)  # regional
        mun_okrug = Munokrug.find(region, uik)
        if mun_okrug:
            filter |= Q(munokrug=mun_okrug)
        return self.filter(filter)

    def current(self):
        #now = now()
        #elect_query = Q(
        #)
        #return self.filter(Q(fromtime__lt=now, totime__gt=now) | elect_query)
        return self.filter(
            date__gt = now() - timedelta(days=10),
            date__lt = now() + timedelta(days=60)
        )
    

class Election(Model):
    """
    Выборы. Региональные могут привязываться к региону. Муниципальные - к мун округу.
    """
    #class Meta():
        #verbose_name = 'Выборы'

    update = base.update
    objects = ElectionQuerySet.as_manager()
    
    id = CharField(max_length=50, default=uuid4, primary_key=True)
    time_created = DateTimeField(default=now, verbose_name='Время создания записи в БД на сервере')

    date = DateField(verbose_name='Дата проведения')

    #subscribed_users = ManyToManyField(
        #'WebsiteUser', related_name='watched_elections', through='ElectionSubscribers', blank=True
    #)
    
    #uiks = ArrayField(PositiveSmallIntegerField(), null=True, blank=True)
    COUNTRIES = [
        ('ru', 'Россия'),
        ('ua', 'Украина'),
        ('bg', 'Беларусь'),
        ('kz', 'Казахстан'),
    ]
    country = CharField(max_length=2, choices=COUNTRIES, default='ru')
    region = ForeignKey('Region', on_delete=SET_NULL, null=True, blank=True, related_name='elections')
    munokrug = ForeignKey('Munokrug', on_delete=SET_NULL, null=True, blank=True)
    name = TextField()
    flags = TextField(null=True, blank=True)

    event_streamers = ManyToManyField(
        'MobileUser', blank=True, through='ElectionMobileUsers', related_name='elections'
    )
    
    def __str__(self):
        return '%s %s' % (self.date, self.name)

    #@classmethod
    #def check(cls, **kwargs):
        #from django.core.checks import Error
        #errors = super().check(**kwargs) or []
            
        #noregion_count = Election.objects.filter(region__isnull=True).count()
        #if noregion_count:
            #errors.append(Error(
                #f'Найдено {noregion_count} выборов с пустым регионом\n'
                #f'Вы можете исправить при помощи команды\n'
                #f' ./manage.py shell_plus --skip-checks -c '
                #'''"print(Election.objects.filter(region__isnull=True).update(region_id='ru_78'))"
#\n''',
                #id='ufo.Election.E001',
            #))
            
        #return errors

class ElectionMobileUsers(Model):
    class Meta:
        unique_together = ('election', 'mobileuser')
        
    election = ForeignKey('Election', on_delete=CASCADE)
    mobileuser = ForeignKey('MobileUser', on_delete=CASCADE)
    


#class ElectionSubscribers(Model):
    #user = ForeignKey('WebsiteUser', on_delete=CASCADE)
    #election = ForeignKey('Election', on_delete=CASCADE)
    
