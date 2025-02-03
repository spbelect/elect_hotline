# -*- coding: utf-8 -*-
from uuid import uuid4

from django.core import checks
from django.db.models import (
    Model, ForeignKey, DateTimeField, BooleanField, CharField, ManyToManyField,
    TextField, PositiveSmallIntegerField, CASCADE, SET_NULL)
from django.db.models import JSONField
from django.utils.timezone import now

from . import base


class TopicQuestions(Model):
    """
    Привязка вопросов к тематическим разделам.
    """
    
    class Meta():
        unique_together = ('topic', 'question')
        ordering = ('sortorder', )

    topic = ForeignKey('QuizTopic', on_delete=CASCADE)
    question = ForeignKey('Question', on_delete=CASCADE)
    sortorder = PositiveSmallIntegerField(default=0)
    time_created = DateTimeField(default=now, verbose_name='Время добавления в этот раздел')


class QuizTopic(Model):
    """
    Тематический раздел анкеты. Например "ДО ГОЛОСОВАНИЯ" или "НА ВЫЕЗДНОМ"
    """
    class Meta():
        ordering = ('sortorder', )

    update = base.update
    
    id = CharField(max_length=50, default=uuid4, primary_key=True)
    time_created = DateTimeField(default=now, verbose_name='Время создания')

    name = TextField()

    country = ForeignKey('Country', related_name='quiztopics', null=True, blank=True, on_delete=SET_NULL)
    questions = ManyToManyField('Question', through=TopicQuestions, blank=True, related_name='topics')
    #elections = ForeignKey('Election', on_delete=CASCADE, null=True, blank=True)

    #form_type = CharField(max_length=20, choices=FORM_TYPE, editable=False)
    #google_form = TextField(null=True, blank=True)

    sortorder = PositiveSmallIntegerField(default=0)

    #def save(self, *args, **kwargs):
        #if not self.elections:
            #self.form_type = FORM_TYPE.GENERAL
        #elif not self.elections.region:
            #self.form_type = FORM_TYPE.FEDERAL
        #elif not self.elections.uiks:
            #self.form_type = FORM_TYPE.REGIONAL
        #else:
            #self.form_type = FORM_TYPE.LOCAL
        #super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    
    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs) or []
            
        try:
            count = QuizTopic.objects.count()
        except Exception as err:
            errors.append(checks.Error(
                f'Не удалось получить количество ответов\n {err}',
                id='ufo.QuizTopic.E001',
                hint='Возможно требуется запустить ./manage.py migrate --skip-checks',
                obj=QuizTopic
            ))
        else:
            if count == 0:
                errors.append(checks.Warning(
                    f'Не найдено ни одного тематического раздела анкеты',
                    hint="Запустите ./scripts/2020_ankety.py",
                    id='ufo.QuizTopic.W001',
                    obj=QuizTopic
                ))

        return errors
    
