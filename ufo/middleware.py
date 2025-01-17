from datetime import timezone, timedelta
from inspect import iscoroutinefunction
from loguru import logger

import django
from django.contrib.auth import models
from django.http import HttpRequest, HttpResponse
from django.utils import translation
from django.utils.decorators import sync_and_async_middleware
from django.utils.functional import cached_property

from .models import Country


class AnonymousUser(django.contrib.auth.models.AnonymousUser):
    def __init__(self, session):
        self.session = session

    def update(self, **kwargs):
        for key, val in kwargs.items():
            self.session[key] = val

    @property
    def language(self):
        return self.session.get('language')

    @property
    def theme(self):
        return self.session.get('theme')

    @property
    def utc_offset(self):
        return self.session.get('utc_offset')

    @property
    def country_id(self):
        return self.session.get('country_id')

    @property
    def tz(self):
        return timezone(timedelta(hours=self.utc_offset))

    @cached_property
    def country(self):
        return Country.objects.get(id=self.country_id)


@sync_and_async_middleware
def anonymous_user_session(get_response):
    """
    Annotate AnonymousUser with persistent properties which are stored in session.

    Add this middleware after django AuthenticationMiddleware:

    MIDDLEWARE = [
        ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'ufo.middleware.anonymous_user_session',
        ...
    ]
    """
    if iscoroutinefunction(get_response):
        async def middleware(request: HttpRequest) -> HttpResponse:
            process_request(request)
            return await get_response(request)
    else:
        def middleware(request: HttpRequest) -> HttpResponse:
            process_request(request)
            return get_response(request)

    return middleware


def process_request(request: HttpRequest) -> None:
    logger.debug(f"{request.method} {request.path} by {request.user}")

    if not request.user.is_authenticated:
        request.session.setdefault('country_id', 'ru')
        request.session.setdefault('utc_offset', 3)
        request.session.setdefault('theme', 'dark')
        request.session.setdefault(
            'language', translation.get_language_from_request(request)
        )

        # Replace with custom AnonymousUser
        request.user = AnonymousUser(request.session)

    translation.activate(request.user.language)
    # print(f'{translation.get_language_from_request(request)=}')
    # print(f'{request.META=}')
    # print(request.user.language)


# def get_user(request):
#     if not hasattr(request, "_cached_user"):
#         request._cached_user = auth.get_user(request)
#     return request._cached_user
#
#
# async def auser(request):
#     if not hasattr(request, "_acached_user"):
#         request._acached_user = await auth.aget_user(request)
#     return request._acached_user


# from django.core.exceptions import ImproperlyConfigured
# from django.utils.functional import SimpleLazyObject
#
#
# def authentication(get_response):
#
#     def middleware(request):
#         if not hasattr(request, "session"):
#             raise ImproperlyConfigured(
#                 "The Django authentication middleware requires session "
#                 "middleware to be installed. Edit your MIDDLEWARE setting to "
#                 "insert "
#                 "'django.contrib.sessions.middleware.SessionMiddleware' before "
#                 "'django.contrib.auth.middleware.AuthenticationMiddleware'."
#             )
#         request.user = SimpleLazyObject(lambda: get_user(request))
#         request.auser = partial(auser, request)
#
#
#     return middleware
