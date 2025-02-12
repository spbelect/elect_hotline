# -*- coding: utf-8 -*-

from uuid import uuid4

from django.core import checks
from django.db.models import (
    Model, ForeignKey, DateTimeField, NullBooleanField, ManyToManyField, TextField, 
    CharField, PositiveSmallIntegerField
)
from django.db.models import JSONField
from django.utils.timezone import now



from . import base


class Question(base.Model):
    """
    Вопрос а анкете. Имеет уникальный id, label, и текст в помощь
    наблюдателю. type - тип ответа на этот вопрос (bool\текст\число)
    """
    
    id = CharField(max_length=50, default=uuid4, primary_key=True)
    time_created = DateTimeField(default=now, verbose_name='Время создания записи в БД на сервере')

    TYPES = (
        ('YESNO', 'Да-Нет'),
        ('NUMBER', 'Число'),
        ('TEXT', 'Текст'),
    )
    type = CharField(max_length=20, choices=TYPES, default='YESNO')

    label = TextField()
    fz67_text = TextField(null=True, blank=True)
    advice_text = TextField(null=True, blank=True)
    example_uik_complaint = TextField(null=True, blank=True)

    # 
    # Показывать этот вопрос в анкете если:
    # * текущие выборы имеют заданные флаги (elect_flags)
    # И
    # * даны разрешающие ответы на ограничивающие вопросы (limiting_questions)
    
    # elect_flags - требуемые флаги выборов для показа этого вопроса.
    # example: ["dosrochka"]
    elect_flags = JSONField(null=True, blank=True)
    
    # limiting_questions - разрешающие условия на ограничивающие вопросы для показа этого вопроса.
    # Возможные значения:
    # { all: [] } - все условия в списке должны быть соблюдены
    # { any: [] } - хотя бы одно условие в списке соблюдено
    """
    example:
    {
        "all": [
            # Возможные условия:
            # answer_equal_to, answer_greater_than, answer_less_than
            {
                "question_id": "ecc1deb3-5fe7-48b3-a07c-839993e4563b", 
                "answer_equal_to": False
            },
            {
                "question_id": "b87436e0-e7f2-4453-b364-a952c0c7842d", 
                "answer_greater_than": 100,
                "answer_less_than": 1000
            }
        ]
    }
    """
    limiting_questions = JSONField(null=True, blank=True)

    # Считать ответ на этот вопрос инцидетом если все заданные условия соблюдены.
    # example: { "answer_equal_to": False }
    incident_conditions = JSONField(null=True, blank=True)

    def __str__(self):
        return '[%s] %s' % (self.get_type_display(), self.label[:30])

    #def full_label(self):
        #if len(self.forms.all()) == 1 and self.forms.all()[0].form_type != FORM_TYPE.GENERAL:
            #return '%s — %s' % (self.forms.all()[0].name, self.label)
        #else:
            #return self.label

    #def get_full_label(self, region_id, uik):
        #if len(self.forms.all()) == 1:
            #return self.full_label()

        #for form in self.forms.all():
            #if form.form_type == FORM_TYPE.LOCAL:
                #if form.elections.region.external_id == int(region_id) and int(uik) in form.elections.uiks:
                    #return '%s — %s' % (form.name, self.label)

        #return self.label


    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs) or []

        topics = Question.objects.all()
        try:
            count = topics.count()
        except:
            return errors
        if count == 0:
            errors.append(checks.Warning(
                f'Не найдено ни одного вопроса анкеты',
                hint="Запустите ./scripts/2020_ankety.py",
                id='ufo.Question.W001',
                obj=Question
            ))

        return errors
