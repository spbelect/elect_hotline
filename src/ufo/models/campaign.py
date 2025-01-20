# -*- coding: utf-8 -*-

from uuid import uuid4
from datetime import datetime, timedelta
import json

from django.db.models import (
    Model, ForeignKey, DateTimeField, NullBooleanField, ManyToManyField, 
    TextField, CharField, PositiveSmallIntegerField, BooleanField, SET_NULL, 
    CASCADE, QuerySet, Q, DateField
)
from django.db.models import JSONField
from django.utils.timezone import now

from . import base 
from .munokrug import Munokrug
from .base import FK

    
class CampaignQuerySet(QuerySet):
    def positional(self, region, uik):
        filter = Q(election__region__isnull=True)  # federal
        filter |= Q(election__region=region, election__munokrug__isnull=True)  # regional
        mun_okrug = Munokrug.find(region, uik)
        if mun_okrug:
            filter |= Q(election__munokrug=mun_okrug)
        return self.filter(filter)

    def current(self):
        #now = datetime.now().astimezone()
        return self.filter(
            election__date__gt = now() - timedelta(days=60),
            election__date__lt = now() + timedelta(days=10)
        )
        #elect_query = Q(
            #election__date__gt=now-timedelta(days=5),
            #election__date__lt=now+timedelta(days=5)
        #)
        #return self.filter(Q(fromtime__lt=now, totime__gt=now) | elect_query)
        #return self.filter(Q(fromtime__lt=now, totime__gt=now))
    
    
class Campaign(Model):
    """
    Кампания наблюдения за выборами.
    """
    
    class Meta:
        unique_together = ('election', 'organization')
        ordering = ('election__date',)
        
    update = base.update
    objects = CampaignQuerySet.as_manager()
    
    id = CharField(max_length=50, default=uuid4, primary_key=True)
    
    time_created = DateTimeField(
        default=now, verbose_name='Время создания записи в БД на сервере'
    )
    
    organization = ForeignKey(
        'Organization', on_delete=CASCADE, related_name='campaigns',
        verbose_name='Координирующая организация'
    )
    election = ForeignKey('Election', on_delete=SET_NULL, null=True, related_name='campaigns')
    
    #fromtime = DateField(blank=True, help_text='lol')
    #totime = DateField(blank=True)
    
    #staff = ManyToManyField('WebsiteUser', related_name='campaigns', through='CampaignStaff')

    ### Если координатор хочет на федеральных выборах ограничить только один регион
    ### для наблюдательской кампании может указать тут.
    ##region = ForeignKey('Region', null=True, blank=True, on_delete=SET_NULL)
    
    #include_org_contacts = BooleanField(default=True)
    
    @property
    def uik_ranges(self):
        return self.organization.uik_ranges(self.election.region)
        
    #def save(self, *args, **kw):
        ###self.fromtime = self.fromtime or self.election.date - timedelta(days=30)
        ###self.totime = self.totime or self.election.date + timedelta(days=10)
        
        ##if self.election.region:
            ### Не-федеральные кампании должны иметь тот же регион что и выборы.
            ##self.region = self.election.region
            
        ##if self.uik_ranges == []:
            ##self.uik_ranges = None
        #super().save(*args, **kw)
        
    def __str__(self):
        #time = self.fromtime or self.election.date
        return f'{self.election} {self.organization}'
    
    #def contacts(self, **kwargs):
        #from .contact import Contact
        #filter = Q(campaign=self)
        ##if self.include_org_contacts:
            ##filter |= Q(organization=self.organization, campaign=None)
        #return Contact.objects.filter(filter, **kwargs)



#class CampaignStaff(Model):
    #class Meta:
        #unique_together = ('campaign', 'member')
        
    #campaign = FK('Campaign')
    #member = FK('WebsiteUser')
    

#from .organization import Phone, ExternalChannel

#class CampaignPhone(Phone):
    #campaign = FK('Campaign', on_delete=CASCADE, related_name='phones')
    
    #def editors(self):
        #return self.campaign.organization.owners.all()

#class CampaignChannel(ExternalChannel):
    #campaign = FK('Campaign', on_delete=CASCADE, related_name='channels')
    
    #def editors(self):
        #return self.campaign.organization.owners.all()
    
