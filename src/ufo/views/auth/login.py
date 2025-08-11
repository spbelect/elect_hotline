from datetime import datetime
from typing import Literal

import django
import httpx
import ska

from anymail.exceptions import AnymailRequestsAPIError
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from ninja import ModelSchema, Query, Form, Schema
from pydantic import UUID4, BaseModel, EmailStr
from ska.contrib.django.ska.decorators import validate_signed_request

import ufo.errors
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
def post_form(request, email: Form[EmailStr], turnstile_token: Form[str]):
    """
    Send email with login link.
    """

    # print(request.body)

    if settings.TURNSTILE_SITE_KEY:
        try:
            response = httpx.post(
                'https://challenges.cloudflare.com/turnstile/v0/siteverify',
                json = {
                    "secret": settings.TURNSTILE_SECRET_KEY,
                    "response": turnstile_token,
                    # remoteip: ip,
                    # idempotency_key: UUID4()
                }
            )

            response.raise_for_status()
            json_response = response.json()
            assert json_response['success'] is True

        except Exception as err:
            raise ufo.errors.HumanVerificationError('Human verification failed') from err

    # request.user.update(**data)
    # print(data.model_dump(exclude_unset=True))

    login_link = ska.sign_url(
        auth_user=email,
        secret_key=settings.SKA_SECRET_KEY,
        url=request.build_absolute_uri('/auth/login/signed')
    )

    message = EmailMessage(
        subject = _('Sign in to Election Hotline'),
        body = _('Link to sign in: {link}').format(link=login_link),
        from_email = f'"Election Hotline" <{settings.DEFAULT_FROM_EMAIL}>',
        to = [email]
    )
    try:
        message.send()
    except AnymailRequestsAPIError:
        if settings.DEBUG:
            raise
        # Hide details from user.
        raise Exception(_('We experienced an error while sending email. Administrators are notified.'))

    if user := WebsiteUser.objects.filter(email=email).first():
        user.update(num_login_emails_sent = user.num_login_emails_sent + 1)

    return render(request, 'views/auth/login.html', {'message': _('Login link sent')})


@validate_signed_request()
@api.html.get('/auth/login/signed')
def login_with_signed_link(request, auth_user: EmailStr):
    """
    Validate signed login link which was generated with ska.sign_url()
    """
    user, created = WebsiteUser.objects.get_or_create(email=auth_user)

    if not user.last_login:
        # Copy user preferences from current request session's AnonymousUser to
        # the WebsiteUser on first login.
        user.init_from_session(request)

    django.contrib.auth.login(request, user)
    #logger.debug(f'WebsiteUser {user} login ok')
    messages.add_message(
        request, messages.INFO,
        _('You have successfully logged in as {user}.').format(user=user)
    )

    return redirect('/')


