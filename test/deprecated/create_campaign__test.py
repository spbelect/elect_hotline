# -*- coding: utf-8 -*-
import re

from datetime import datetime, date, timedelta
from collections import OrderedDict

import pendulum
import pytest

from django.conf import settings
from django.core import mail
from django.urls import reverse
from django.test import TestCase
from django.test import override_settings
from django.utils.timezone import localtime, now
from model_bakery.baker import make
from playwright.sync_api import Playwright, Page, expect
from unittest.mock import Mock, patch, ANY

from rest_framework.serializers import ValidationError, DateTimeField
#from rest_framework.settings import api_settings
from rest_framework.status import HTTP_200_OK
# from nose.plugins.attrib import attr

from ufo.models import (
    Region, Country, WebsiteUser, Election, Campaign, Organization, Contact, OrgBranch,
    WebsiteUser
)
from ..base import BaseTestCase, MSK, ru, spb, msk


@pytest.mark.uitest
def create_campaign_scenario__test(spb, msk, live_server, page):
    # GIVEN actual federal Election
    make(Election,
        id='election-id-fed-actual',
        name='Выборы президента',
        date = date.today() + timedelta(days=10),
    )
    # AND 2 actual regional Elections
    make(Election,
        id='election-id-spb-actual',
        name='Выборы губернатора спб',
        date = date.today() + timedelta(days=10),
        region=spb
    )
    make(Election,
        id='election-id-msk-actual',
        name='Выборы губернатора мск',
        date = date.today() + timedelta(days=10),
        region=msk
    )

    # AND 2 old Elections
    make(Election,
        id='election-id-fed-2013',  name='Федеральные Выборы 2013', date=date(2013, 4, 4),
    )
    old_spb_election = make(Election,
        id='election-id-spb-2013',  name='Cпб Выборы 2013', date=date(2013, 4, 4), region=spb
    )

    ######
    # WHEN user opens home page
    page.goto(f"{live_server}/feed/answers/")

    # AND clicks login
    page.get_by_label("Меню").first.click()
    # page.get_by_text("Меню").click()
    expect(page.get_by_role("link", name="Вoйти")).to_be_visible()
    page.get_by_role("link", name="Вoйти").click()

    # AND submits login email
    expect(page.get_by_placeholder("Введите email")).to_be_visible()
    page.get_by_placeholder("Введите email").click()
    page.get_by_placeholder("Введите email").fill("test@example.com")
    page.get_by_role("button", name="Отправить").click()

    # THEN he sees email send success message
    expect(page.get_by_text("Ссылка отправлена на электронную почту")).to_be_visible()
    # page.locator("#LoginModal").get_by_text("Закрыть").click()

    # AND 1 email have been sent
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    # to user's email address
    assert email.to == ['test@example.com']
    # AND email contains login link
    assert email.body.startswith(f'Ссылка для входа на сайт: {live_server}/auth/login/')

    login_link = re.findall('(http://[^ ]+)', email.body)[0]

    # WHEN user opens login link in the browser
    page.goto(login_link)

    # THEN he should see successfull login message
    expect(page.get_by_text("Вы успешно вошли как")).to_be_visible()
    # import ipdb; ipdb.sset_trace()


    ######
    # WHEN he opens organizations page
    page.get_by_label("Меню").first.click()
    # expect(page.get_by_role("link", name="Организации")).to_be_visible()
    page.get_by_role("link", name="Организации").click()

    # AND creates new organization in MSK region
    page.get_by_role("button", name="Создать").click()

    page.get_by_placeholder("Название организации").fill("штаб петрова")

    select = page.get_by_label("Выберите регионы в которых действует организация")
    select.click()
    select.locator('div').filter(has_text=re.compile(r"^Москва$")).click()

    page.get_by_role("button", name="OK").click()

    # THEN manage org section should be visible
    expect(page.get_by_label("Управление организацией штаб петрова")).to_be_visible()


    ##########
    # WHEN user opens campaigns page
    page.get_by_label("Меню").first.click()
    page.get_by_label("Управление кампаниями").click()

    # THEN federal active elections campaigns should be visible and startable
    expect(page.get_by_label("Начать кампанию Выборы президента")).to_be_visible()
    # AND MSK active elections campaigns should be visible and startable
    expect(page.get_by_label("Начать кампанию Выборы губернатора мск")).to_be_visible()

    # AND SPB active elections campaigns should NOT be visible and startable
    expect(page.get_by_label("Начать кампанию Выборы губернатора спб")).to_have_count(0)

    # WHEN he clicks start campaign Выборы президента
    page.get_by_label("Начать кампанию Выборы президента").click()

    # THEN campaign settings should be visible
    expect(page.get_by_label("Кампания наблюдения Выборы президента")).to_be_visible()

    # WHEN he clicks add contact
    page.get_by_label("Добавить контакт для Выборы президента").click()

    # AND fills name and phone
    # page.get_by_role("textbox", name="Название контакта").click()
    page.get_by_role("textbox", name="Название контакта").fill("Коллцентр")
    page.get_by_role("textbox", name="Номер телефона или ссылка").fill("+77777")
    page.get_by_role("button", name="OK").click()

    # THEN Phone should be added to the Campaign
    expect(
        page.get_by_label("Кампания наблюдения Выборы президента").get_by_label('Phone')
    ).to_contain_text("+77777")


    #######
    # WHEN user clicks select uiks
    page.get_by_text('Указать номера УИК').click()

    # THEN MSK region uik config button should be visible
    expect(page.get_by_label('Указать УИК Москва')).to_be_visible()
    # AND SPB region uik config button should not exist
    expect(page.get_by_label('Указать УИК Санкт-Петербург')).to_have_count(0)

    # WHEN user clicks edit uiks for MSK
    page.get_by_label('Указать УИК Москва').click()

    # THEN MSK uik ranges modal window should be visible
    msk_uiks_form = page.get_by_label('Диапазоны номеров УИК Москва')
    expect(msk_uiks_form).to_be_visible()

    # AND only 1 range input row is visible
    expect(msk_uiks_form.get_by_label('Диапазон', exact=True)).to_have_count(1)

    # WHEN user clicks "more" button
    page.get_by_label('Добавить диапазон').click()

    # THEN 2 range input rows should be visible
    expect(msk_uiks_form.get_by_label('Диапазон', exact=True)).to_have_count(2)

    # WHEN user fills two uik ranges
    page.get_by_placeholder("От").first.fill('2')
    page.get_by_placeholder("До").first.fill('21')

    page.get_by_placeholder("От").nth(1).fill('500')
    page.get_by_placeholder("До").nth(1).fill('1500')

    # AND clicks OK
    page.get_by_label('Сохранить диапазоны Москва').click()

    # AND user clicks select uiks
    page.get_by_text('Указать номера УИК').click()

    # THEN saved uik ranges should be visible
    expect(page.get_by_text("Москва УИК: 2-21, 500-1500")).to_be_visible()


    ######
    # WHEN he opens staff page
    page.get_by_label("Меню").first.click()
    page.get_by_role("link", name="Персонал").click()

    # AND invites buddy
    page.get_by_label("Введите email для приглашения").fill("buddy@example.org")
    page.get_by_label("Отправить приглашение").click()

    # THEN sending success message should be visible
    expect(page.get_by_text("Приглашение отправлено на электронную почту")).to_be_visible()

    # THEN secondemail have been sent
    assert len(mail.outbox) == 2
    email = mail.outbox[-1]
    # to user's email address
    assert email.to == ['buddy@example.org']
    # AND email body has invitation text
    assert email.body.startswith(
        f'test@example.com приглашает вас присоединиться к организации штаб петрова'
    )
    # AND email body has invitation link
    assert len(re.findall(f'({live_server}/auth/login/[^ ]+)', email.body)) == 1

    # print(login_link)
    # print('')
