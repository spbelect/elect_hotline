#!/usr/bin/env python
import json
import os
import re
import django
import csv
import sys
from collections import defaultdict, namedtuple, OrderedDict

from functools import lru_cache

import django
from bs4 import BeautifulSoup
from requests import get
from click import Context, confirm, command, option, group, argument, progressbar

import click
import environ


Context.get_usage = Context.get_help  # show full help on error


env = environ.Env()
SRCDIR = environ.Path('..')
sys.path.insert(0, str(SRCDIR))
env.read_env(SRCDIR('env-local'))
os.chdir(str(SRCDIR))

if os.path.exists('../settings_local.py'):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_local")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    
django.setup()

from ufo.models import Region, Tik


tik_ranges = {
    '1': [('1', '103')],
    '2': [('104', '198')],
    '10': [('199', '251')],
    '14': [('252', '312')],
    '22': [('330', '413')],
    '11': [('414', '511')],
    '17': [('512', '575'), ('2283', '2285'), ('2318', '2319'), (2373, 2375)],
    '3': [('576', '632'), ('645', '756')],
    '7': [('633', '644'), ('757', '825')],
    '21': [('826', '900')],
    '4': [('901', '972')],
    '25': [('973', '1058')],
    '6': [('1058', '1138')],
    '26': [('1145', '1219')],
    '15': [('1220', '1238'), ('2293', '2295')],
    '13': [('1239', '1278')],
    '19': [('1279', '1366')],
    '27': [('1367', '1421')],
    '5': [('1422', '1544')],
    '24': [('1545', '1611')],
    '18': [('1612', '1673')],
    '8': [('1674', '1723')],
    '12': [('1724', '1792')],
    '9': [('1793', '1866')],
    '28': [('1867', '1948')],
    '20': [('1949', '2034')],
    '23': [('2035', '2103')],
    '29': [('2104', '2179')],
    '16': [('2180', '2232')],
    '30': [('2233', '2282')],
}

#regions = json.load(open('regions.json'))

#for region in regions:
    #print(region)
    
    #Region.objects.update_or_create(id=f'ru_{region["fields"]["external_id"]}', defaults={
        #'name':region['fields']['name']
    #})



def stats():
    data = csv.reader(open('stats.csv'), delimiter=',')
    next(data, None)  # skip the headers
    
    Row = namedtuple('row', 'tik, raion, uik, voters, mn_in, mn_out, koib')
    new = lambda x: Row(*x[:len(Row._fields)])
    tiks = defaultdict(list)
    for row in map(new, data):
        #tiks[row.tik].append(row._asdict())
        #row.uik = int(row.uik)
        tiks[row.tik].append(row)
    return OrderedDict((tik, ranges(rows)) for tik, rows in sorted(tiks.items(), key=lambda x: int(x[0])))
    #for row in data:
        #try:
            #Row(*row[:len(Row._fields)])
        #except:
            #print(row)
            #raise
    #return {new(x).uik: new(x) for x in data}

def uiks2():
    data = open('uiks spb.txt')
    next(data, None)
    tiks = defaultdict(list)
    Row = namedtuple('row', 'uik')
    
    for line in data:
        n, tik, uik = line.split('\t')
        tiks[tik].append(Row(uik.split()[0]))
        #print(list(data))
    return OrderedDict((tik, ranges(rows)) for tik, rows in sorted(tiks.items(), key=lambda x: int(x[0])))
    
    
def ranges(rows):
    ranges = []
    last_uik = None
    rows = sorted(rows, key=lambda x: int(x.uik))
    for row in rows:
        #if not last_uik:
            #ranges.append((row.uik: row.uik))
        if ranges and int(row.uik) == int(last_uik) + 1:
            ranges.append((ranges.pop()[0], row.uik))
        else:
            ranges.append((row.uik, row.uik))
        last_uik = row.uik
    return ranges
      
from pprint import pprint
#pprint(sorted([(tik, ranges(rows)) for tik, rows in stats().items()], key=lambda x: int(x[0])))
#pprint((tik, ranges(rows)) for tik, rows in uiks2().items())
#pprint(dict(uiks2()))
#pprint(dict(stats()))

#[]

            
@group()
def cli(**kw):
    """ Manage regions. """
    pass
    
    
@cli.command()
@option('--clean', '-c', is_flag=True, default=False, help='Delete existing regions.')
#@argument('index', default='all')
def populatedb(**kw):
    """ Populate django db tiks. """
    
        
    spb = Region.objects.get(id='ru_78')

    for tik, ranges in tik_ranges.items():
        #ztik = tik.zfill(2)
        Tik.objects.update_or_create(name=f'№{tik}', region=spb, defaults=dict(
            email = f'letterik{tik.zfill(2)}@spbik.spb.ru',
            uik_ranges = [[int(x), int(y)] for x,y in ranges]
        ))
        print(tik)
        
        
    #cik_regions = json.load(open('scripts/cik_regions.json'))
    ##print(cik_regions)
    ##sys.exit(1)

    #if set(tz) - set(cik_regions.values()):
        #print(f'Регионы отсутствуют на сайте ГАС: {sorted(set(tz) - set(cik_regions.values()))}')
        #sys.exit(1)
    #if set(cik_regions.values()) - set(tz):
        #print(f'Регионы отсутствуют в списке timezones: {sorted(set(cik_regions.values()) - set(tz))}')
        #sys.exit(1)
            
    #Region.objects.all().delete()
    #for id, name in cik_regions.items():
        #print(name)
        
        #Region.objects.update_or_create(id=f'ru_{id}', defaults={
            #'name': name,
            #'utc_offset': int(tz[name])
        #})
    print('ok')


#@cli.command()
#def scrape(**kw):
    #""" Парсить регионы с сайта ГАС выборов, сохранить в cik_regions.json"""
    #cik_regions = {}
    #soup = get_html('http://www.izbirkom.ru/region/izbirkom')
    #select = soup.find('select',  attrs={'name':"actual_regions_subjcode"})
    #for option in select.children:
        ## исключим Усть-Ордынский Бурятский ао - он теперь в составе Иркутской обл
        #if option.text == 'Усть-Ордынский Бурятский автономный округ':
            #continue
        
        #id = option.attrs.get('value')
        #if id.isdigit() and not id == '0':
            #cik_regions[int(id)] = option.text
            
    #if set(tz) - set(cik_regions.values()):
        #print(f'Регионы отсутствуют на сайте ГАС: {sorted(set(tz) - set(cik_regions.values()))}')
        #sys.exit(1)
    #if set(cik_regions.values()) - set(tz):
        #print(f'Регионы отсутствуют в списке timezones: {sorted(set(cik_regions.values()) - set(tz))}')
        #sys.exit(1)
    #json.dump(cik_regions, open('scripts/cik_regions.json', 'w+'), indent=2, ensure_ascii=False)
    #print(f'{len(cik_regions)} regions scraped successfully. Saved to scripts/cik_regions.json')

        
if __name__ == '__main__':
    cli()
    
