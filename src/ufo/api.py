import logging
from django.conf import settings
from django.http import Http404
from django.shortcuts import render

# from loguru import logger
import pydantic
from ninja import NinjaAPI
import ninja.errors
# from ninja.renderers import BaseRenderer


# class TemplateRenderer(BaseRenderer):
#     media_type = "text/html"
#
#     def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
#         return django.shortcuts.render(request, f'http_error.html', data)



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
def pydantic_validation_errors(request, exc):
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
def exc_error(request, exc):
    if settings.DEBUG:
        raise exc
    logging.exception(exc)
    return render(
        request, "views/http_error.html", {'error': exc}, status=500
    )

@html.exception_handler(Http404)
def error_404(request, exc):
    logging.exception(exc)
    return render(
        request, "views/http_error.html", {'error': exc}, status=404
    )

@html.exception_handler(ninja.errors.HttpError)
def http_error(request, exc):
    if settings.DEBUG:
        raise exc
    logging.exception(exc)
    return render(
        request, "views/http_error.html", {'error': exc}, status=exc.status_code
    )
