import logging
from django.conf import settings
from django.shortcuts import render

# from loguru import logger
from ninja import NinjaAPI
from ninja.errors import ValidationError, HttpError
# from ninja.renderers import BaseRenderer


# class TemplateRenderer(BaseRenderer):
#     media_type = "text/html"
#
#     def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
#         return django.shortcuts.render(request, f'http_error.html', data)



# api = NinjaAPI(renderer=TemplateRenderer())
html = NinjaAPI(urls_namespace='html')

@html.exception_handler(ValidationError)
def validation_errors(request, exc):
    if settings.DEBUG:
        logging.error(exc)
    # import ipdb; ipdb.sset_trace()
    return render(
        request, "views/validation_error.html", {'errors': exc.errors}, status=422
    )


@html.exception_handler(Exception)
def exc_error(request, exc):
    if settings.DEBUG:
        raise exc
    return render(
        request, "views/http_error.html", {'error': exc}, status=500
    )

@html.exception_handler(HttpError)
def http_error(request, exc):
    if settings.DEBUG:
        raise exc
    return render(
        request, "views/http_error.html", {'error': exc}, status=exc.status_code
    )
