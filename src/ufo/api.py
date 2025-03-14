import logging
import django.http

from django.conf import settings
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

# from loguru import logger
import pydantic
# from ninja import Router
from ninja import NinjaAPI, Redoc
import ninja.errors
# from ninja.renderers import BaseRenderer


# class TemplateRenderer(BaseRenderer):
#     media_type = "text/html"
#
#     def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
#         return django.shortcuts.render(request, f'http_error.html', data)


v4 = NinjaAPI(
    urls_namespace='v4',
    title="Mobile API",
    version='v4',
    description="API for mobile app. Allows to retrieve list of elections, questions, and to submit answers."
    # docs=Redoc()
)

# api = NinjaAPI(renderer=TemplateRenderer())
html = NinjaAPI(urls_namespace='html')

@html.exception_handler(ninja.errors.ValidationError)
def ninja_validation_errors(request, exc):
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
    ValidationError raised in a view.
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
    """
    if settings.DEBUG:
        raise exc
    logging.exception(exc)
    return render(
        request, "views/http_error.html", {'error': exc}, status=exc.status_code
    )
