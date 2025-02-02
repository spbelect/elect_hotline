# -*- coding: utf-8 -*-

from uuid import uuid4
from datetime import datetime, timedelta
import json

from django.db.models import (
    Model, ForeignKey, DateTimeField, NullBooleanField, ManyToManyField, 
    TextField, CharField, PositiveSmallIntegerField, BooleanField, SET_NULL, 
    CASCADE, QuerySet, Q
)
from django.db.models import JSONField
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinLengthValidator
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_pydantic_field import SchemaField
from pydantic import conint, conlist, constr, Json

from .base import FK
from . import base 
from . import munokrug 


    
class Organization(Model):
    """
    Координирующая организация. Например "Штаб Иванова" или "Наблюдатели Петербурга".
    """
    update = base.update
    
    id = CharField(max_length=50, default=uuid4, primary_key=True)
    time_created = DateTimeField(default=now, verbose_name='Время создания в БД')
    #slug = CharField(max_length=50, unique=True)

    name = CharField(max_length=1000, validators=[
        MinLengthValidator(3, _('Name must contain at least 3 characters'))
    ])
    shortname = CharField(max_length=50, blank=True, null=True)
    
    # Регионы, в которых организация действует. Только исключительные органицации являются
    # федеральными (действует во всех регионах), остальные могут указать не больше 2.
    regions = ManyToManyField(
        'Region', blank=True, related_name='organizations', through='OrgBranch'
    )
    
    # TODO: remove in favor of Election.event_streamers ?
    event_streamers = ManyToManyField('MobileUser', blank=True)

    creator = ForeignKey('WebsiteUser', related_name='owned_orgs', on_delete=CASCADE)
    
    @cached_property
    def admins(self):
        from .websiteuser import WebsiteUser
        return WebsiteUser.objects.filter(
            Q(orgmembership__in=OrgMembership.objects.filter(organization=self, role='admin'))
            | Q(pk=self.creator.pk)
        ).distinct()
        
    members = ManyToManyField(
        'WebsiteUser', through='OrgMembership', blank=True, verbose_name='Члены',
        related_name='organizations'
    )
    

    def uik_ranges(self, region):
        try:
            branch = self.branches.get(region=region)
        except ObjectDoesNotExist:
            return None
        return branch.uik_ranges
        
    #def moderators(self):
        #return

    def __str__(self):
        return self.name

    def save(self, *a, **kw):
        super().save(*a, **kw)
        OrgMembership.objects.update_or_create(
            organization=self,
            user=self.creator,
            defaults={'role':'admin'}
        )


Range = conlist(conint(gt=0, lt=9999), min_length=2, max_length=2)

class OrgBranch(Model):
    update = base.update
    
    class Meta:
        unique_together = ('organization', 'region')
    
    organization = ForeignKey('Organization', on_delete=CASCADE, related_name='branches')
    region = ForeignKey('Region', on_delete=CASCADE, related_name='org_branches')
    
    # Пример: [[0, 99],] или [[400, 449], [2100, 2105]]
    uik_ranges = JSONField(null=True, blank=True)
    
    # uik_ranges: conlist(Range, max_length=10) = SchemaField(null=True, blank=True)

    def get_uik_ranges(self):
        return ['{}-{}'.format(*x) for x in self.uik_ranges or []]
    
    def save(self, *args, **kw):
        if self.uik_ranges == []:
            self.uik_ranges = None
        super().save(*args, **kw)
    
    
class OrgMembership(Model):
    update = base.update
    
    class Meta:
        unique_together = ('organization', 'user')
    
    organization = ForeignKey('Organization', on_delete=CASCADE)
    user = ForeignKey('WebsiteUser', on_delete=CASCADE)
    ROLES = [
        ('operator', 'Оператор'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
        ('invited', 'Приглашен'),
    ]
    role = CharField(max_length=10, choices=ROLES, default='operator')
    
    time_created = DateTimeField(default=now, verbose_name='Время назначения')


#class OrganizationOwner(Model):
    #organization = ForeignKey('Organization', on_delete=CASCADE)
    #user = ForeignKey('WebsiteUser', on_delete=CASCADE)
    
    #time_created = DateTimeField(default=now, verbose_name='Время назначения')


class OrgJoinApplication(Model):
    """ Заявка на вступление в организацию. """
    
    update = base.update
    
    class Meta:
        unique_together = ('organization', 'user')
    
    organization = ForeignKey('Organization', on_delete=CASCADE, related_name='join_requests')
    user = ForeignKey('WebsiteUser', on_delete=CASCADE, related_name='org_join_requests')
    
    time_created = DateTimeField(default=now, verbose_name='Время создания заявки')

    def save(self, *a, **kw):
        # TODO: send email to org owners.
        #if not self.pk:
            #self.organization.owners
        super().save(*a, **kw)
