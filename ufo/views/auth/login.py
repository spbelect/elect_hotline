from datetime import datetime
from typing import Literal

import django
import ska

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from ninja import ModelSchema, Query, Form, Schema
from pydantic import UUID4, BaseModel, EmailStr
from ska.contrib.django.ska.decorators import validate_signed_request

from ufo import api
from ufo.models import WebsiteUser

#
# class EmailSchema(Schema):
#     email: EmailStr


@api.html.get('/auth/login')
def get_form(request):
    """ Display login options form. """
    return render(request, 'views/auth/login.html')


@api.html.post('/auth/login')
def post_form(request, email: Form[EmailStr]):
    """
    Send email with login link.
    """

    # print(data)
    # import ipdb; ipdb.sset_trace()
    # print(request.body)
    # data = data.dict(exclude_unset=True)
    # print(data)

    # request.user.update(**data)
    # print(data.model_dump(exclude_unset=True))

    link = ska.sign_url(
        auth_user=email,
        secret_key=settings.SKA_SECRET_KEY,
        url=request.build_absolute_uri('/auth/login/signed')
    )

    message = EmailMessage(
        subject = _('Sign in to Election Hotline'),
        body = _('Link to sign in: {link}').format(link=link),
        from_email = f'"Election Hotline" <{settings.DEFAULT_FROM_EMAIL}>',
        to = [email]
    )
    message.send()

    return render(request, 'views/auth/login.html', {'message': _('Login link sent')})


@validate_signed_request()
@api.html.get('/auth/login/signed')
def login_with_signed_link(request, auth_user: EmailStr):
    """
    Validate signed login link which was generated with ska.sign_url()
    """
    user, created = WebsiteUser.objects.get_or_create(email=auth_user)

    if created:
        user.init(request)

    django.contrib.auth.login(request, user)
    #logger.debug(f'WebsiteUser {user} login ok')
    messages.add_message(
        request, messages.INFO,
        _('You have successfully logged in as {user}.').format(user=user)
    )

    return redirect('/newsite')


