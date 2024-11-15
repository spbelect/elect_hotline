#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import json
import os
import random
import re
import sys
import traceback

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import django
from rich.progress import track
from typer import Typer, Option, confirm
from typing_extensions import Annotated


MSK = ZoneInfo('Europe/Moscow')

app = Typer(no_args_is_help=True)


os.chdir(Path(__file__).joinpath('../..').resolve())  # src dir

os.environ.setdefault("DJANGO_SETTINGS_MODULE",
    "settings_local" if Path('settings_local.py').exists() else "settings"
)

django.setup()


@app.command()
def mock(
    delete: Annotated[bool, Option(help="Delete existing answers")] = False
):
    """ Populate django db answers. """

    confirm(
        "This will create mock answers in the database!\n"
        "Are you sure you want to proceed?", abort=True
    )

    from ufo.models import Answer, MobileUser, Question, int16

    if delete:
        Answer.objects.all().delete()

    alice = MobileUser.objects.update_or_create(app_id='alice', defaults=dict(
        first_name="Alice",
        last_name="Alisson",
        role='observer',
        email='alice@example.com',
        region_id='ru_78',
        uik=1
    ))[0]

    bob = MobileUser.objects.update_or_create(app_id='bob', defaults=dict(
        first_name="Bob",
        last_name="Bobston",
        role='psg',
        email='bob@example.com',
        region_id='ru_1',
        uik=2
    ))[0]


    for user in (alice, bob):
        questions = Question.objects.filter(type='YESNO')

        for question in track(questions, description=f"{user}..."):
            if ord(question.id[-1]) % 3:
                continue  # skip some random questions

            Answer.objects.create(
                question=question,
                revoked=bool(random.choice([0,1])),
                value_bool=True,
                is_incident=not bool(ord(question.id[-2:-1]) % 3),
                appuser=user,
                region=user.region,
                uik=user.uik,
                role=user.role,
                uik_complaint_status=int16('не подавалась') if random.choice([0,1]) else int16('отказ принять жалобу'),
                timestamp=datetime(2024, 9, 9).replace(tzinfo=MSK),
            )

    print(f'{Answer.objects.filter(appuser=alice).count()=}')
    print(f'{Answer.objects.filter(appuser=bob).count()=}')
    print(f'{Answer.objects.count()=}')
    print('ok')



if __name__ == '__main__':
    app()
    
