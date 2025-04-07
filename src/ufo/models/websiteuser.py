# -*- coding: utf-8 -*-
from datetime import timezone, timedelta

from django.core import validators, checks
from django.core.mail import send_mail

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    Model, ForeignKey, DateField, BooleanField, PositiveSmallIntegerField, TextField,
    CharField, SET_NULL, CASCADE, IntegerField, DateTimeField, EmailField, Q, SmallIntegerField,
    JSONField, TextChoices, PositiveIntegerField
)
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import gettext, gettext_lazy as _

from . import base 
from .region import Country


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **kw):
        """
        Creates and saves a User with the given email and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **kw)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **kw):
        default = {'is_staff': False, 'is_superuser': False}
        return self._create_user(email, password, dict(default, **kw))

    def create_superuser(self, email, password, **kw):
        kw.setdefault('is_staff', True)
        kw.setdefault('is_superuser', True)

        if kw.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if kw.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **kw)


class WebsiteUser(AbstractBaseUser, PermissionsMixin):
    """
    Оператор колл-центра.
    
    This model was initially copied from django.contrib.auth.models.AbstractUser.
    Username field is removed. We use email for authentication.
    """
    class Meta():
        verbose_name = _('user')
        verbose_name_plural = _('users')


    update = base.update
    
    # NOTE: Following two fields - `password` and `last_login` are inherited from the
    # base model: django.contrib.auth.base_user.AbstractBaseUser
    #   password = models.CharField(_('password'), max_length=128)
    #   last_login = models.DateTimeField(_('last login'), blank=True, null=True)


    first_name = CharField(_('first name'), max_length=30, blank=True)
    last_name = CharField(_('last name'), max_length=30, blank=True)
    email = EmailField(_('email address'), max_length=100, unique=True)
    is_staff = BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = DateTimeField(_('date joined'), default=now)
    
    # List of strings for ex. ['User x joined org y', 'bla bla']
    unread_notifications = JSONField(default=list, blank=True)
    
    # # Website settings
    # COUNTRIES = [
    #     ('ru', 'Россия'),
    #     ('ua', 'Украина'),
    #     ('bg', 'Беларусь'),
    #     ('kz', 'Казахстан'),
    # ]
    # country = CharField(max_length=2, choices=COUNTRIES, default='ru')

    class Languages(TextChoices):
        en = 'en', _("English")
        ru = 'ru', _("Russian")

    language = CharField(_('Language'), max_length=2, choices=Languages, default=Languages.en)

    country = ForeignKey('Country', null=True, on_delete=SET_NULL)
    utc_offset = SmallIntegerField(default=3)
    theme = CharField(_('Theme'), max_length=30, default='dark')
    photo = TextField(_('Photo'), null=True, blank=True)

    #app_ids = ArrayField(CharField(max_length=20), null=True, blank=True)
    
    num_login_emails_sent = PositiveIntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    #REQUIRED_FIELDS = ['email']

    async def acountry(self):
        return await Country.objects.aget(id=self.country_id)

    @cached_property
    def tz(self):
        return timezone(timedelta(hours=self.utc_offset))


    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._previous_last_login = self.last_login

    def save(self, **kw):
        if self.country is None:
            self.country = Country.objects.get(id='ru')

        if self.unread_notifications is None:
            self.unread_notifications = []

        super().save(**kw)
        
        if self._previous_last_login is None and self.last_login is not None:
            # This is the first user login. User was previously created likely when
            # she was invited.

            from .organization import OrgMembership
            # Update organization memberships from invited to actual role.
            for membership in OrgMembership.objects.filter(user=self, role='invited'):
                membership.update(role='operator')

                # Notify org owner about new user joined.
                membership.organization.creator.unread_notifications.append(
                    gettext('Пользователь {user.email} присоединился к организации'
                    ' {org.name}'.format(user=self, org=membership.organization))
                )
                membership.organization.creator.save()

                # Delete join request if exist.
                membership.organization.join_requests.filter(user=self).delete()


    def init_from_session(self, request):
        """
        Called from auth login view when user is logged in first time.
        """

        # Copy settings from session.
        self.update(
            country=request.user.country,
            language=request.user.language,
            utc_offset=request.user.utc_offset,
            theme=request.user.theme
        )


    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.last_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @cached_property
    def disclosed_appusers(self):
        return set()
        from .mobileuser import MobileUser
        #from .election import Election 
        #from .campaign import Campaign 
        #from .organization import Organization 
        appusers = MobileUser.objects.filter(elections__campaigns__organization__members=self)
        #import ipdb; ipdb.sset_trace()
        return set(appusers.values_list('id', flat=True))
    
    @cached_property
    def managed_orgs(self):
        from .organization import OrgMembership, Organization
        return Organization.objects.filter(
            Q(orgmembership__in=OrgMembership.objects.filter(user=self, role='admin'))
            | Q(creator=self)
        ).distinct()
    

    @classmethod
    def check(cls, **kwargs):
        messages = super().check(**kwargs) or []

        bad_country = WebsiteUser.objects\
            .exclude(country__in='ru ua kz bg'.split())\
            .values_list('country_id', flat=True)

        try:
            count = len(bad_country)
        except Exception as err:
            messages.append(checks.Error(
                f'Не удалось получить количество Пользователей\n {err}',
                id='ufo.WebsiteUser.E001',
                hint='Возможно требуется запустить ./manage.py migrate --skip-checks',
                obj=WebsiteUser
            ))
            return messages

        if count != 0:
            messages.append(checks.Error(
                f'В базе есть пользователи с неверными значениями country: '
                f'{",".join(str(x) for x in set(bad_country))}',
                id='ufo.WebsiteUser.E002',
                obj=WebsiteUser
            ))

        no_country = WebsiteUser.objects.filter(country__isnull=True).count()

        if no_country != 0:
            messages.append(checks.Error(
                f'В базе есть пользователи с пустым значениями country',
                id='ufo.WebsiteUser.E003',
                hint=f'Вы можете исправить при помощи команды\n'
                f' ./manage.py shell_plus --skip-checks -c '
                '''"print(WebsiteUser.objects.filter(country__isnull=True).update(country_id='ru'))"
                ''',
                obj=WebsiteUser
            ))

        return messages
