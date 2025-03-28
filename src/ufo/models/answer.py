# -*- coding: utf-8 -*-
from uuid import uuid4

from django.conf import settings
from django.db.models import (
    ForeignKey, DateTimeField, BooleanField, UUIDField, QuerySet, Manager, SET_NULL, CASCADE,
    CharField, IntegerField, Model, TextField, SmallIntegerField as Int16)
from django.db.models import JSONField, CheckConstraint, Q
from django.utils.timezone import now
from loguru import logger

from . import base
from .base import FK, int16
from .websiteuser import WebsiteUser


# TODO: record user ip to ban
#IPV4 = 'xxx.xxx.xxx.xxx'

class Answer(base.Model):
    """
    Answer описывает ответ данный юзером на вопрос в анкете.
    """
    class Meta():
        ordering = ('-timestamp', )  # Новые вверху

        constraints = [
            CheckConstraint(
                name="ufo_Answer_appuser_or_operator",
                violation_error_code="ufo.Answer.creator_not_null",
                violation_error_message="Ответ должен иметь создателя - оператора или " \
                    "пользователя приложения",
                condition=(
                    Q(appuser__isnull=True,  operator__isnull=False) |
                    Q(appuser__isnull=False, operator__isnull=True )
                ),
            )
        ]

        
    id = CharField(max_length=40, default=uuid4, primary_key=True)
    time_created = DateTimeField(default=now, verbose_name='Время создания записи в БД на сервере')

    question = ForeignKey('Question', on_delete=CASCADE)
    
    # Время когда событие произошло.
    timestamp = DateTimeField(verbose_name='Когда пользователь ввел ответ')

    revoked = BooleanField('отозвано', default=False)
    is_incident = BooleanField()
    role = CharField(max_length=15)

    region = ForeignKey('Region', null=True, on_delete=SET_NULL)
    uik = Int16()

    UIK_COMPLAINT_STATUS = [(int16(x), x) for x in [
        'не подавалась',
        'отказ принять жалобу',
        'отказ рассмотрения жалобы',
        'отказ выдать копию решения',
        'ожидание решения комиссии',
        'получено неудовлетворительное решение',
        'получено удовлетворительное решение',
    ]]
    TIK_COMPLAINT_STATUS = [(int16(x), x) for x in [
        'не подавалась',
        'ожидает модератора',
        'отклонено',
        'email отправлен',
    ]]
    uik_complaint_status = Int16(choices=UIK_COMPLAINT_STATUS, default=int16('не подавалась'))
    tik_complaint_status = Int16(choices=TIK_COMPLAINT_STATUS, default=int16('не подавалась'))
    tik_complaint_text = TextField(null=True, blank=True)
    time_tik_email_request_created = DateTimeField(null=True, blank=True)
    
    # appuser или operator - кем было добавлено
    appuser = FK('MobileUser', related_name='answers')
    operator = FK('WebsiteUser')

    #ipv4 = CharField(max_length=len(IPV4))  # [TODO]

    value_bool = BooleanField(null=True, blank=True)
    value_int = IntegerField(null=True, blank=True)
    #value_text = TextField(null=True, blank=True)
    
    # Когда пользователя банят, его ответы помечаются удаленными
    banned = BooleanField(default=False)

    def save(self,*a, **kw):
        self.full_clean()
        super().save(*a, **kw)
        
    def get_value(self):
        if self.question.type == 'YESNO':
            if self.value_bool is None:
                return 'Неизвестно'
            if self.value_bool is True:
                return 'Да'
            
            return 'Нет'
        else:
            return self.value_int
        
    #def userprofile(self):
        #profiles =Answerobjects.filter(data__type='userprofile', data__app_id=self.data['app_id'])
        #Userprofile.objects.
        #return profiles.order_by('-timestamp').values('data')[0]['data']

    def uik_images(self):
        return self.images.filter(type__in=('uik_complaint', 'uik_reply')).values_list('filename', flat=True)
    
    def tik_images(self):
        return self.images.filter(type__in=('tik_complaint', 'tik_reply')).values_list('filename', flat=True)
    
    @property
    def tik(self):
        from .tik import Tik
        return Tik.find(self.region, self.uik)
    
    def get_email_recipients(self):
        from .campaign import Campaign
        from .tik import Tik, TikSubscription
        from .websiteuser import WebsiteUser
        
        tik = Tik.find(self.region, self.uik)
        #campaigns = Campaign.objects.positional(self.region, self.uik).current()
        logger.debug(f'TIK {tik}, {campaigns}')
        
        if tik and campaigns:
            # Отправить копию членам тик.
            tik_memberships = TikSubscription.objects.filter(
                tik=tik
            )
                
            bcc = list(WebsiteUser.objects.filter(
                tik_memberships__in=tik_memberships,
            ).values_list('email', flat=True))
        else:
            bcc = []
            
        if tik and tik.email and not settings.FAKE_TIK_EMAILS:
            to = [tik.email]
            #to = [settings.ADMIN_EMAIL]
            bcc.append(self.appuser.email)
        else:
            to = [self.appuser.email]
            bcc.append(settings.ADMIN_EMAIL)
        
        if to[0] in bcc:
            bcc.remove(to[0])
            
        return to, bcc
            

    def send_tik_complaint(self):
        from django.core.mail import EmailMessage
        from django.core import validators
        from .tik import Tik
        try:
            validators.validate_email(self.appuser.email)
        except validators.ValidationError as e:
            sentry_sdk.capture_exception(e)
            return

        tik = Tik.find(self.region, self.uik)
        if not tik or not tik.email:
            return

        #to, bcc = self.get_email_recipients()
        subscriptions = list(tik.subscriptions.filter(unsubscribed=False).values_list('email', flat=True))

        email = EmailMessage(
            subject = f'УИК {self.uik} Жалоба',
            body = self.tik_complaint_text,
            from_email = f'"{self.appuser.last_name} {self.appuser.first_name}" <{settings.DEFAULT_FROM_EMAIL}>',
            to = [tik.email],
            bcc = subscriptions + [self.appuser.email],
            reply_to = [self.appuser.email],
            #headers={'Message-ID': 'foo'},
        )
        for image in self.images.filter(deleted_by_user=False):
            #url = 'https://s3.eu-central-1.amazonaws.com/ekc-uploads/433b7b0206d0d23306fcaebea1c11840Screenshot_20190112_132357_x.jpg'
            response = get(f'https://s3.eu-central-1.amazonaws.com/ekc-uploads/{image.filename}')

            #response = get(url, stream=True)
            #email.attach(basename(url), BytesIO(response.content))
            email.attach(image.filename, response.content)
        email.send()
        #email.to = self.appuser.email
        #email.bcc =

        self.update(tik_complaint_status=int16('email отправлен'))
        logger.debug(f'Email sent to {email.to + email.bcc}')
        #return to + bcc


    @classmethod
    def check(cls, **kwargs):
        from django.core.checks import Error
        errors = super().check(**kwargs) or []
            
        answers = Answer.objects.exclude(uik_complaint_status__in=dict(Answer.UIK_COMPLAINT_STATUS))
        try:
            count = answers.count()
        except:
            return errors
        if count > 0:
            errors.append(Error(
                f'Найдено {count} ответов с невалидным значением uik_complaint_status\n'
                f'Валидные значения: {dict(Answer.UIK_COMPLAINT_STATUS)}\n'
                f'Невалидные: {set(answers.values_list("uik_complaint_status", flat=True))}',
                #hint='No hint',
                id='ufo.Answer.E001',
            ))
            
        answers = Answer.objects.exclude(tik_complaint_status__in=dict(Answer.TIK_COMPLAINT_STATUS))
        try:
            count = answers.count()
        except:
            return errors
        if count > 0:
            errors.append(Error(
                f'Найдено {count} ответов с невалидным значением tik_complaint_status\n'
                f'Валидные значения: {dict(Answer.TIK_COMPLAINT_STATUS)}\n'
                f'Невалидные: {set(answers.values_list("tik_complaint_status", flat=True))}',
                #hint='No hint',
                #obj=self,
                id='ufo.Answer.E002',
            ))
            
        noregion_count = Answer.objects.filter(region__isnull=True).count()
        if noregion_count:
            errors.append(Error(
                f'Найдено {noregion_count} ответов с пустым регионом\n'
                f'Вы можете исправить при помощи команды\n'
                f' ./manage.py shell_plus --skip-checks -c '
                '''"print(Answer.objects.filter(region__isnull=True).update(region_id='ru_78'))"
\n''',
                #hint='No hint',
                id='ufo.Answer.E003',
            ))
            
        return errors
    
    
#class AnswerMobileUserComment(Model):
    ## TODO: пока не используется
    #created = DateTimeField(default=now)
    #event = ForeignKey('Answer', on_delete=CASCADE)
    #timestamp = DateTimeField()
    #text = TextField()
    
    #class Meta:
        #ordering = ('timestamp',)


class AnswerImage(base.Model):
    created = DateTimeField(default=now)
    answer = FK('Answer', related_name='images')
    TYPES = [
        ('uik_complaint', 'Подаваемые в УИК жалобы'),
        ('uik_reply', 'Ответы, решения от УИК'),
        ('tik_complaint', 'Подаваемые в ТИК жалобы'),
        ('tik_reply', 'Ответы, решения от ТИК'),
    ]
    type = CharField(max_length=20, choices=TYPES)
    filename = TextField()
    timestamp = DateTimeField()
    deleted_by_user = BooleanField(default=False)
    
    class Meta:
        ordering = ('timestamp',)
    
