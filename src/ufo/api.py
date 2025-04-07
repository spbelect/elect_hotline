import logging

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

# from loguru import logger
import django.http
import ninja.errors
import ninja.renderers
import pydantic
import sentry_sdk
# from ninja import Router
from ninja import NinjaAPI, Redoc


###
### Mobile app api
###

v4 = NinjaAPI(
    urls_namespace='v4',
    title="Mobile API",
    version='v4',
    description="API for mobile app. Allows to retrieve list of elections, questions, and to submit answers."
    # docs=Redoc()
)


###
### HTML frontend api
###

class StringToHttpResponse(ninja.renderers.BaseRenderer):
    """ When the view returns a string, convert it to HttpResponse. """
    media_type = "text/html"

    def render(self, request, data: str, *, response_status: int) -> HttpResponse:
        return HttpResponse(data)


html = NinjaAPI(urls_namespace='html', renderer=StringToHttpResponse())


@html.exception_handler(ninja.errors.ValidationError)
def ninja_validation_errors(request, exc):
    """
    Ninja ValidationError raised in a view.

    ninja.errors.ValidationError has attribure `errors` which is a list of dicts.
    Unlike pydantic.ValidationError, which has `errors() -> list[dict]` method.
    """
    if settings.DEBUG:
        logging.exception(exc)
    else:
        logging.debug(exc)
    return render(
        request, "views/validation_error.html", {
            'errors': [
                dict(
                    err,
                    input_name = [x for x in err['loc'] if isinstance(x, str)][-1]
                ) for err in exc.errors
            ]
        }, status=422
    )


@html.exception_handler(pydantic.ValidationError)
def pydantic_validation_errors(request, exc: pydantic.ValidationError):
    """
    Pydantic ValidationError raised in a view.

    Most of the time we let Ninja validate input data. But for types which ninja doesn't
    support, (e.g. Json, conlist) we Create Pydantic model and validate it inside a view.
    For example, see /ufo/views/organizations/id/branches/post_form.py
    In this case pydantic.ValidationError is raised instead of ninja.errors.ValidationError.

    ninja.errors.ValidationError has attribure `errors` which is a list of dicts.
    Unlike pydantic.ValidationError, which has `errors() -> list[dict]` method.
    """
    if settings.DEBUG:
        logging.exception(exc)
    else:
        logging.debug(exc)
    return render(
        request, "views/validation_error.html", {
            'errors': [
                dict(
                    err,
                    input_name = [x for x in err['loc'] if isinstance(x, str)][-1]
                ) for err in exc.errors()
            ]
        }, status=422
    )


@html.exception_handler(Exception)
def exc_error(request, exc: Exception):
    """
    Exception raised in a view.
    """
    sentry_sdk.capture_exception(exc)

    if settings.DEBUG and not request.headers.get('X-Alpine-Request') == 'true':
        raise exc
    logging.exception(exc)
    return render(
        request,
        "views/http_error.html",
        {'error': exc if settings.DEBUG else _('Server error occured')},
        status=500
    )


@html.exception_handler(django.http.Http404)
def error_404(request, exc: django.http.Http404):
    """
    Http404 raised in a view.
    """
    logging.exception(exc)
    return render(
        request, "views/http_error.html", {'error': exc}, status=404
    )


@html.exception_handler(ninja.errors.HttpError)
def http_error(request, exc: ninja.errors.HttpError):
    """
    HttpError raised in a view.
    TODO: Currently this includes Unauthorized error 401. Should we create separate
    HttpError subclass for it?
    """

    sentry_sdk.capture_exception(exc)

    if settings.DEBUG:
        raise exc
    logging.exception(exc)
    return render(
        request, "views/http_error.html", {'error': exc}, status=exc.status_code
    )
