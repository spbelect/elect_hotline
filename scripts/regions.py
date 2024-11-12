#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import json
import os
import re
import sys
import traceback

#from os.path import abspath
from functools import lru_cache

import django
from requests import get
from click import Context, confirm, command, option, group, argument, progressbar

import click
import environ


Context.get_usage = Context.get_help  # show full help on error


env = environ.Env()
SRCDIR = environ.Path(__file__).path('../..')
sys.path.insert(0, str(SRCDIR))
env.read_env(SRCDIR('env-local'))
os.chdir(str(SRCDIR))

if os.path.exists('../settings_local.py'):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_local")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    
print(f'Using django settings {os.environ["DJANGO_SETTINGS_MODULE"]}.py')
django.setup()


from ufo.models import Region, Country

for id, name in [
            ('ru', 'Russia'),
            ('ua', 'Ukraine'),
            ('bg', 'Belarus'),
            ('kz', 'Kazakhstan'),
        ]:
    Country.objects.update_or_create(id=id, defaults={'name':name})


@lru_cache()
def get_html(url):
    from bs4 import BeautifulSoup
    
    for retry in range(1, 10):
        print('try %d get %s' % (retry, url))
        response = get(url)
        if response.status_code == 200 and response.text:
            soup = BeautifulSoup(response.text, 'html.parser')
            if soup.find('select', attrs={'name':"actual_regions_subjcode"}):
                return soup
    print('Max reties exceeded')
    sys.exit(1)

            

# взято с http://www.phcode.ru/chasovyie-zonyi-rossii
tz = [x.split('\t') for x in '''
Калининградское время (1-я часовая зона)
Калининградская область 	МСК-1	UTC+2:00

Московское время (2-я часовая зона)
Москва 	МСК	UTC+3:00
Санкт-Петербург 	МСК	UTC+3:00
Севастополь 	МСК	UTC+3:00
Архангельская область 	МСК	UTC+3:00
Белгородская область 	МСК	UTC+3:00
Брянская область 	МСК	UTC+3:00
Владимирская область 	МСК	UTC+3:00
Волгоградская область 	МСК	UTC+3:00
Вологодская область 	МСК	UTC+3:00
Воронежская область 	МСК	UTC+3:00
Ивановская область 	МСК	UTC+3:00
Кабардино-Балкарская Республика 	МСК	UTC+3:00
Калужская область 	МСК	UTC+3:00
Карачаево-Черкесская Республика 	МСК	UTC+3:00
Кировская область 	МСК	UTC+3:00
Костромская область 	МСК	UTC+3:00
Краснодарский край 	МСК	UTC+3:00
Курская область 	МСК	UTC+3:00
Ленинградская область 	МСК	UTC+3:00
Липецкая область 	МСК	UTC+3:00
Московская область 	МСК	UTC+3:00
Мурманская область 	МСК	UTC+3:00
Ненецкий автономный округ 	МСК	UTC+3:00
Нижегородская область 	МСК	UTC+3:00
Новгородская область 	МСК	UTC+3:00
Орловская область 	МСК	UTC+3:00
Пензенская область 	МСК	UTC+3:00
Псковская область 	МСК	UTC+3:00
Республика Адыгея (Адыгея) 	МСК	UTC+3:00
Республика Дагестан 	МСК	UTC+3:00
Республика Ингушетия 	МСК	UTC+3:00
Республика Калмыкия 	МСК	UTC+3:00
Республика Карелия 	МСК	UTC+3:00
Республика Коми 	МСК	UTC+3:00
Республика Крым 	МСК	UTC+3:00
Республика Марий Эл 	МСК	UTC+3:00
Республика Мордовия 	МСК	UTC+3:00
Республика Северная Осетия-Алания 	МСК	UTC+3:00
Республика Татарстан (Татарстан)	МСК	UTC+3:00
Ростовская область 	МСК	UTC+3:00
Рязанская область 	МСК	UTC+3:00
Саратовская область 	МСК	UTC+3:00
Смоленская область 	МСК	UTC+3:00
Ставропольский край 	МСК	UTC+3:00
Тамбовская область 	МСК	UTC+3:00
Тверская область 	МСК	UTC+3:00
Тульская область 	МСК	UTC+3:00
Чеченская Республика 	МСК	UTC+3:00
Чувашская Республика - Чувашия 	МСК	UTC+3:00
Ярославская область 	МСК	UTC+3:00

(NEW 26.10.14)
Самарское время (3-я часовая зона)
Астраханская область 	МСК+1	UTC+4:00
Самарская область 	МСК+1	UTC+4:00
Удмуртская Республика 	МСК+1	UTC+4:00
Ульяновская область 	МСК+1	UTC+4:00

Екатеринбургское время (4-я часовая зона)
Курганская область 	МСК+2	UTC+5:00
Оренбургская область 	МСК+2	UTC+5:00
Пермский край 	МСК+2	UTC+5:00
Республика Башкортостан 	МСК+2	UTC+5:00
Свердловская область 	МСК+2	UTC+5:00
Тюменская область 	МСК+2	UTC+5:00
Ханты-Мансийский автономный округ 	МСК+2	UTC+5:00
Челябинская область 	МСК+2	UTC+5:00
Ямало-Ненецкий автономный округ 	МСК+2	UTC+5:00

Омское время (5-я часовая зона)
Омская область 	МСК+3	UTC+6:00

Красноярское время (6-я часовая зона)
Алтайский край 	МСК+4	UTC+7:00
Красноярский край 	МСК+4	UTC+7:00
Кемеровская область 	МСК+4	UTC+7:00
# NOTE: Новосибирская область на сайте неправильно отнесена к UTC+6:00
Новосибирская область 	МСК+4	UTC+7:00
Республика Алтай 	МСК+4	UTC+7:00
Республика Тыва 	МСК+4	UTC+7:00
Республика Хакасия 	МСК+4	UTC+7:00
# NOTE: Томская область на сайте неправильно отнесена к UTC+6:00
Томская область 	МСК+4	UTC+7:00

Иркутское время (7-я часовая зона)
Иркутская область 	МСК+5	UTC+8:00
Республика Бурятия 	МСК+5	UTC+8:00

Якутское время (8-я часовая зона)
Амурская область 	МСК+6	UTC+9:00
Забайкальский край 	МСК+6	UTC+9:00
Республика Саха (Якутия) 	МСК+6	UTC+9:00
# NOTE: в якутии три часовых пояса - UTC+9:00 UTC+10:00 UTC+11:00
# Будем счтитать что интересен только город Якутск

Владивостокское время (9-я часовая зона)
Еврейская автономная область 	МСК+7	UTC+10:00
Приморский край 	МСК+7	UTC+10:00
Хабаровский край 	МСК+7	UTC+10:00
Магаданская область 	МСК+7	UTC+10:00

(NEW 26.10.14)
Среднеколымское время (10-я часовая зона)
Сахалинская область 	МСК+8	UTC+11:00

(NEW 26.10.14)
Камчатское время (11-я часовая зона)
Камчатский край 	МСК+9	UTC+12:00
Чукотский автономный округ 	МСК+9	UTC+12:00
'''.split('\n') if '	' in x]

tz = {x[0].strip(): int(x[-1][4:-3]) for x in tz}

 
            
@group()
def cli(**kw):
    """ Manage regions. """
    pass
    
    
@cli.command()
@option('--delete', '-d', is_flag=True, default=False, help='Delete existing regions.')
#@argument('index', default='all')
def populatedb(**kw):
    """ Populate django db regions. """
    
    if kw.get('delete'):
        msg = 'This will delete all regions the database!\nAre you sure you want to proceed?'
        if not click.confirm(msg):
            return
        
    cik_regions = json.load(open('scripts/cik_regions.json'))
    #print(cik_regions)
    #sys.exit(1)

    if set(tz) - set(cik_regions.values()):
        print(f'Регионы отсутствуют на сайте ГАС: {sorted(set(tz) - set(cik_regions.values()))}')
        sys.exit(1)
    if set(cik_regions.values()) - set(tz):
        print(f'Регионы отсутствуют в списке timezones: {sorted(set(cik_regions.values()) - set(tz))}')
        sys.exit(1)
        
    if kw.get('delete'):
        Region.objects.all().delete()
        
    for id, name in cik_regions.items():
        print(name)
        
        Region.objects.update_or_create(id=f'ru_{id}', defaults={
            'name': name,
            'utc_offset': int(tz[name]),
            'country_id': 'ru'
        })
    print('ok')


@cli.command()
def scrape(**kw):
    """ Парсить регионы с сайта ГАС выборов, сохранить в cik_regions.json"""
    cik_regions = {}
    soup = get_html('http://www.izbirkom.ru/region/izbirkom')
    select = soup.find('select',  attrs={'name':"actual_regions_subjcode"})
    for option in select.children:
        # исключим Усть-Ордынский Бурятский ао - он теперь в составе Иркутской обл
        if option.text == 'Усть-Ордынский Бурятский автономный округ':
            continue
        
        id = option.attrs.get('value')
        if id.isdigit() and not id == '0':
            cik_regions[int(id)] = option.text.replace('город ', '')
            
    if set(tz) - set(cik_regions.values()):
        print(f'Регионы отсутствуют на сайте ГАС: {sorted(set(tz) - set(cik_regions.values()))}')
        sys.exit(1)
    if set(cik_regions.values()) - set(tz):
        print(f'Регионы отсутствуют в списке timezones: {sorted(set(cik_regions.values()) - set(tz))}')
        sys.exit(1)
    json.dump(cik_regions, open('scripts/cik_regions.json', 'w+'), indent=2, ensure_ascii=False)
    print(f'{len(cik_regions)} regions scraped successfully. Saved to scripts/cik_regions.json')

        
if __name__ == '__main__':
    cli()
    
