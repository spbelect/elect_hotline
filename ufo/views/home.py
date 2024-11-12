from datetime import datetime
from typing import Literal

import django

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from ninja import ModelSchema, Query, Form, Schema
from pydantic import UUID4, BaseModel, EmailStr

from ufo import api
from ufo.models import WebsiteUser



@api.html.get('/')
def home(request):
    return render(request, 'views/home.html')
