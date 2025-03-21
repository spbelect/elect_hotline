"""
OAUTH2 flow:
1. User clicks "Sign in" link which sends
    GET /auth/google/start
    Backend generates and stores session secret num and redirects to external auth page
    GET https://accounts.google.com/o/oauth2/auth

2. Google auth page redirects to
    GET /auth/google/success?code={code}&state={secret}&error={error}
    Backend checks secret and errors query parameers

3. Backend fetches JWT token via sending POST request to
    POST https://oauth2.googleapis.com/token?code={code}&client_id={client_id}&...
    Backend logs in WebsiteUser wich has email equal to token['email']
"""
import secrets
from datetime import datetime
from string import ascii_letters, digits
from typing import Literal
from urllib.parse import urlencode

import django
import httpx
import logging
import jwt

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import gettext as _
from ninja import ModelSchema, Query, Form, Schema
from ninja.errors import HttpError
from pydantic import UUID4, BaseModel, EmailStr

from ufo import api
from ufo.models import WebsiteUser


@api.html.get('/auth/google/start')
def google_start(request) -> HttpResponseRedirect:
    """
    ### Step 1 ###

    Store secret number in request.session on the server, and redirect user to
    the google account authentication page.
    """
    request.session["google_oauth2_state_secret"] = ''.join(
        secrets.choice(ascii_letters + digits) for i in range(30)
    )

    return redirect("https://accounts.google.com/o/oauth2/auth?{params}".format(
        params = urlencode({
            "response_type": "code",
            "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
            "redirect_uri": f'{request.build_absolute_uri("/auth/google/success")}',
            "scope": " ".join([
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
                "openid",
            ]),
            "state": request.session["google_oauth2_state_secret"],
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "select_account",
        })
    ))


class AccessCode(Schema):
    """
    Parameters returned by google to Step 2 in GET request query to google_callback():
    /auth/google/success?code=..&state=..&error=...
    """
    # Code that must be provided in a POST request to fetch JWT token at Step 3.
    code: str | None = None

    # State parameter is a string which must be checked to match the secret number stored
    # previously in the user session at Step 1.
    state: str | None = None

    # Any error occured during user authentication on google side.
    error: str | None = None


@api.html.get('/auth/google/success')
def google_callback(request, data: Query[AccessCode]) -> HttpResponseRedirect:
    """
    ### Step 2 ###

    Oauth2 callback that google redirects to after the user grants access.
    """
    if data.error:
        logging.error(f'{data.error}')
        raise HttpError(401, _("Authentication failed"))

    # Check AccessCode.state to be equal to the secret number previously stored at Step 1.
    if data.state != request.session.get("google_oauth2_state_secret"):
        logging.error(f'{data.state=} != {request.session.get("google_oauth2_state_secret")}')
        raise HttpError(401, _('Authentication failed'))

    del request.session["google_oauth2_state_secret"]

    #### Step 3 ###

    try:
        # Fetch JWT token which has actual user email and name.
        response = httpx.post('https://oauth2.googleapis.com/token', params={
            "code": data.code,
            "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            "redirect_uri": f'{request.build_absolute_uri("/auth/google/success")}',
            "grant_type": "authorization_code",
        })

        if not response.is_success:
            raise Exception(_("Failed to obtain access token from Google."))

        id_token = response.json()["id_token"]

        token = jwt.decode(jwt=id_token, options={"verify_signature": False})

        # JWT joken sample
        # {
        #     'iss': 'https://accounts.google.com',
        #     'azp': '123456-1h6j26k46k36k6.apps.googleusercontent.com',
        #     'aud': '97934603-h36j37k8j2k.apps.googleusercontent.com',
        #     'sub': '12334567890',
        #     'email': 'john@gmail.com',
        #     'email_verified': True,
        #     'at_hash': 'D7mk4jhklglt-63',
        #     'name': 'John Doe',
        #     'picture': 'https://lh3.googleusercontent.com/a/HKJ35k_52Jfh=s96-c',
        #     'given_name': 'John',
        #     'family_name': 'Doe',
        #     'iat': 1730758614,
        #     'exp': 1730762214
        # }

    except Exception as err:
        raise HttpError(401, _('Authentication failed')) from err


    user, created = WebsiteUser.objects.get_or_create(email=token['email'])

    if not user.last_login:
        # Copy user preferences from current request session's AnonymousUser to
        # the WebsiteUser on first login.
        user.init_from_session(request)

    django.contrib.auth.login(request, user)

    return redirect('/answers/history')

