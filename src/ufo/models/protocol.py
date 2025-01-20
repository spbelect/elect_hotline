# -*- coding: utf-8 -*-
import re

from collections import OrderedDict

from django.conf import settings
from django.db.models import (
    Model, ForeignKey, DateField, BooleanField, PositiveSmallIntegerField, TextField,
    IntegerField, CharField, SET_NULL, DateTimeField
)
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils.timezone import now

import requests

from . import base 


def get_entries(url):
    return re.sub('\=[^&]+', '', url).split('?')[1].split('&')


class Protocol(Model):
    """
    Данные итогового протокола от пользователя. Заполняются при поступлении событий.
    После полного заполнения отправляет в гугл-форму.
    В поле data - словарь input_id: value
    """
    class Meta():
        verbose_name = 'Протокол'

    # mapping {input_id: value}
    data = JSONField(verbose_name='Данные', default=dict)

    region = ForeignKey('Region', on_delete=SET_NULL, null=True, blank=True)
    uik = IntegerField()

    #appform = ForeignKey('appform', on_delete=SET_NULL, null=True, blank=True)

    app_id = CharField(max_length=20)
    fio = TextField()
    phone = TextField()

    complete = BooleanField(default=False)
    #google_submitted = BooleanField(default=False)

    def __str__(self):
        return 'Протокол %s' % (self.pk)

    def ordered_data(self):
        result = OrderedDict()
        for n, input in enumerate(self.appform.inputs.all()):
            result[input.label] = self.data.get(str(input.id))
        return result

    def send(self):
        if not int(self.region.external_id) == 78:
            return
        if not self.appform.google_form:
            return
        if not settings.SUBMIT_GOOGLE_PROTO:
            return
        fields = get_entries(self.appform.google_form)
        form_data = {
            fields[0]: self.uik,
            fields[1]: self.phone,  # phone
            fields[2]: self.fio,  # fio
            fields[3]: 'app_id:%s' % self.app_id,  # comment
        }

        for n, input in enumerate(self.appform.inputs.all()):
            form_data[fields[n + 4]] = self.data[str(input.id)]

        headers = {
            'Referer':'https://docs.google.com/forms/d/152CTd4VY9pRvLfeACOf6SmmtFAp1CL750Sx72Rh6HJ8/viewform',
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36'
        }

        url = self.appform.google_form.split('?')[0].replace('viewform', 'formResponse')
        response = requests.post(url, data=form_data, headers=headers)


    def save(self, *args, **kwargs):
        known_ids = set(map(str, self.appform.inputs.values_list('id', flat=True)))
        if known_ids.difference(set(self.data)):
            self.complete = False
        else:
            self.complete = True

        return super().save(*args, **kwargs)
