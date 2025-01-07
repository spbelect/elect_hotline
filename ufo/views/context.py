# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date, timezone
# from gettext import GNUTranslations

import django
from django.apps import apps
from django.contrib.messages.constants import DEFAULT_LEVELS
from django.contrib.messages.api import get_messages
from django.contrib.humanize.templatetags import humanize
from django.core.checks import register, Tags
from django.db.models import Max, Q
# from django.shortcuts import render
from django.templatetags.static import static
from django.urls import reverse
from django.utils import translation
from jinja2 import Environment

import utils
import ufo

from ..models import (
    Answer, Region, WebsiteUser, Munokrug, MobileUser, Election, Campaign, int16, Contact
)
from utils.templatetags.utils import plural




def jinja_env(**kwargs) -> Environment:
    """
    Static context variables independent of request

    Add it to TEMPLATES in settings.py:

    TEMPLATES = [{
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'OPTIONS': {
            'environment': 'ufo.views.conext.jinja_env',
        }
    }]
    """

    env = Environment(**kwargs)
    env.install_gettext_translations(django.utils.translation)
    # env.add_extension(LanguageExtension)

    # Populate context with Model classes
    env.globals.update({m.__name__: m for m in apps.all_models['ufo'].values()})

    env.globals.update({
        "plural": utils.templatetags.utils.plural,
        'humanize': django.contrib.humanize.templatetags.humanize,
        'int16': int16,
        'static': static,
        'version': ufo.__version__

        # 'url': reverse,
    })
    return env


def context_processor(request) -> dict:
    """
    Returns request-dependent context variables.

    Add it to TEMPLATES in settings.py:

    TEMPLATES = [{
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'OPTIONS': {
            'context_processors': [
                'ufo.views.conext.context_processor'
            ],
        }
    }]
    """

    return {}

    actual_regions = []

    if request.user.is_authenticated:
        # Кампании которые прошли недавно или пройдут в будущем
        actual_campaigns = Campaign.objects.filter(
            organization__in = request.user.organizations.all(),
            election__date__gt = date.today() - timedelta(days=10)
        )
        if all(x.election.region for x in actual_campaigns):
            # Нет федеральных кампаний. Покажем в меню ссылки на ленту всех регионов где
            # есть актуальная кампания.
            actual_regions = Region.objects.distinct().filter(
                elections__campaigns__in=actual_campaigns
            )
        else:
            # Есть федеральная кампания. Покажем в меню ссылки на ленту всех регионов орг-цй.
            actual_regions = Region.objects.filter(
                organizations__in=request.user.organizations.all()
            )

    return {
        'menu': {
            # Показать в меню ссылки на ленту всех "актуальных" регионов где в ближайшее
            # время прошли или пройдут выборы.
            'actual_regions': actual_regions,
        },
        # 'regions': Region.objects.filter(id__startswith='ru_'),
        'notifications': list(notifications(request)),

    }


def notifications(request) -> list[str]:

    messages = []

    if request.user.is_authenticated:
        messages.extend(request.user.unread_notifications)

        if request.user.managed_orgs:
            future_campaigns = Campaign.objects.filter(
                organization__in = request.user.managed_orgs,
                election__date__gt=date.today()
            )
            if future_campaigns:
                org_contacts = {'organization__in': request.user.managed_orgs, 'campaign__isnull': True}
                future_contacts = Contact.objects.filter(
                    Q(campaign__in=future_campaigns) | Q(**org_contacts)
                )
                if not future_contacts.exists():
                    # Нет контактов у ораганизвции и в предстоящих кампаниях.
                    messages.append(
                        f'<a href="/old/html/organizations/manage/{request.user.managed_orgs.first().pk}/campaigns/">'
                            'Укажите контакты'
                        '</a> организации чтобы наблюдатели могли с вами связаться.'
                    )
            else:
                # Нет предстоящих кампаний.
                messages.append(
                    f'<a href="/old/html/organizations/manage/{request.user.managed_orgs.first().pk}/campaigns/">'
                        'Создайте кампанию'
                    '</a> по наблюдению на предстоящих выборах чтобы наблюдатели увидели ваши контакты'
                    ' в мобильном приложении.'
                )

    return messages

