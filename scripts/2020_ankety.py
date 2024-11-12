#!/usr/bin/env python
import os
import re
import django
import csv
import json
import environ
import sys


env = environ.Env()
SRCDIR = environ.Path(__file__).path('../..')
sys.path.insert(0, str(SRCDIR))
env.read_env(SRCDIR('env-local'))
os.chdir(str(SRCDIR))


if os.path.exists('settings_local.py'):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_local")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    
print(f'Using django settings {os.environ["DJANGO_SETTINGS_MODULE"]}.py')
django.setup()


from ufo.models import Question, QuizTopic, TopicQuestions, Election


doc = csv.reader(open('scripts/ankety2019.csv'))
next(doc, None)  # skip CSV header

TopicQuestions.objects.all().delete()

#filee =
dependants = []


for n, row in enumerate(doc):
    if row[0].isupper():
        print(n, row)
        #curform = row[0]
        topic, _ = QuizTopic.objects.update_or_create(name=row[0], defaults={'sortorder': n})
        continue

    #print(row[0])
    #type, alarm = row[0].split(' ')[-2:]
    #import ipdb; ipdb.sset_trace()
    try:
        label, type, alarm, srok = re.search('(.*) type:(.*) alarm:=(\w*)(?: srok_obj_tik:(.*))?', row[0]).groups()
    except:
        print(row)
        raise
    #label = ' '.join(row[0].split(' ')[:-2])
    #alarm = alarm.split(':=')[-1].strip()
    if alarm == 'нет':
        alarm = False
    elif alarm == 'да':
        alarm = True
    else:
        alarm = None
        
    if alarm is not None:
        alarm = {"answer_equal_to": alarm}
    
    #if srok:
        #print(srok, type, alarm, label)
    
    #continue
    help = row[1]
    if row[3]:
        help += '\nРабочий блокнот по выборам Губернатора СПб\n' + row[3]
    if row[5]:
        help += '\nПрактические советы\n' + row[5]
    if row[6]:
        help += '\n' + row[6]  # постановления ЦИК
    if 'да' in type:
        question = Question.objects.update_or_create(
            label=label, 
            type='YESNO',
            defaults={'fz67_text': help, 'incident_conditions': alarm}
        )[0]
        #print('\n'.join(row[3:5]))
    elif 'исло' in type:
        question = Question.objects.update_or_create(
            label=label, 
            type='NUMBER',
            defaults={'fz67_text': help, 'incident_conditions': alarm}
        )[0]
    else:
        print(row)
        print('!!!')
        break

    TopicQuestions.objects.update_or_create(question=question, topic=topic, defaults={'sortorder':n})
    
    if "Ваш участок оборудован КОИБ" in label:
        koib_question = question
        
    if 'КОИБ' in topic.name and "Ваш участок оборудован КОИБ" not in label:
        question.update(limiting_questions={'all': [
            {'question_id': str(koib_question.id), 'answer_equal_to': True}
        ]})
        
#print(dependants)
#Question.objects.filter(label__contains="Ваш участок оборудован КОИБ").\
    #update(limiting_questions=json.dumps(dependants))

print(f'OK. {Question.objects.count()} вопросов в базе.')
