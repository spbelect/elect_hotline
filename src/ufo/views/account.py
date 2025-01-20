from datetime import datetime
from typing import Literal

import django

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import translation
from ninja import ModelSchema, Query, Form
from pydantic import UUID4, BaseModel

from ufo import api
from ufo.models import WebsiteUser


class UserSchema(ModelSchema):
    class Meta:
        model = WebsiteUser
        fields = ['utc_offset', 'country', 'theme', 'language']
        fields_optional = '__all__'


@api.html.get('/account/form')
def get_form(request):
    return render(request, 'views/account.html')


@api.html.post('/account/form')
def post_form(request, data: Form[UserSchema]):
    # if request.user.is_authenticated:
    print(data)
    # import ipdb; ipdb.sset_trace()
    print(request.body)
    # data = data.dict(exclude_unset=True)
    # print(data)

    # request.user.update(**data)
    print(data.model_dump(exclude_unset=True))
    request.user.update(**data.model_dump(by_alias=True, exclude_unset=True))

    translation.activate(request.user.language)
    # else:
    #     request.session['utc_offset'] = data.utc_offset
    #     request.session['country_id'] = data.country

    # messages.add_message(request, messages.INFO, 'Настройки сохранены.')

    return render(request, 'views/account.html')

