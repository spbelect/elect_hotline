#!/usr/bin/env python
import json
import os
import re
import django
import csv
from collections import defaultdict, namedtuple, OrderedDict

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
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

#spb = Region.objects.get(id='ru_78')

#for tik, ranges in tik_ranges.items():
    ##ztik = tik.zfill(2)
    #Tik.objects.update_or_create(name=f'№{tik}', region=spb, defaults=dict(
        #email = f'letterik{tik.zfill(2)}@spbik.spb.ru',
        #uik_ranges = [[int(x), int(y)] for x,y in ranges]
    #))
    #print(tik)
    
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
    data = open('spb-mo.txt')
    #next(data, None)
    tiks = defaultdict(list)
    Row = namedtuple('row', 'uik')
    
    m1 = 'выборы депутатов муниципального совета внутригородского муниципального образования санкт-петербурга муниципального округа '
    m2 = 'выборы депутатов муниципального совета внутригородского муниципального образования санкт-петербурга'
    m3 = 'выборы депутатов муниципального совета муниципального образования'
    
    end = len('шестого созыва')
    mo = None
    uiks = OrderedDict()
    for line in data:
        line = line.replace('муниципальный округ', '').strip()
        #print(line )
        if 'окружная' in line:
            continue
        if line.startswith('выборы'):
            if line.startswith(m1):
                mo = line[len(m1):-end].strip()
            if line.startswith(m2):
                mo = line[len(m2):-end].strip()
            if line.startswith(m3):
                mo = line[len(m3):-end].strip()
            #print(mo)
            uiks[mo] = []
            #if not line.endswith():
                #print(line)
            #print(line)
        else:
            uiks[mo].append(line.split(' ')[0])
        #n, tik, uik = line.split('\t')
        #tiks[tik].append(Row(uik.split()[0]))
        ##print(list(data))
        
    print(json.dumps(uiks, ensure_ascii=False))
    #print(json.dumps(uiks, indent=2, ensure_ascii=False))
    #return OrderedDict((tik, ranges(rows)) for tik, rows in sorted(tiks.items(), key=lambda x: int(x[0])))
    
    
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

uiks2()
#[]
