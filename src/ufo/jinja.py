from django.apps import apps
from django.conf import settings
from django.http import HttpResponse
from django.template.backends.utils import csrf_input_lazy, csrf_token_lazy

import django.contrib.humanize.templatetags.humanize
import django.template.backends.jinja2
import django.db.models
import django.templatetags.static
import django.utils.translation
import jinja2.ext
import pendulum

import ufo
import utils.templatetags.utils

from .models import int16


class Environment(jinja2.Environment):
    """
    Defines constants and functions used in templates.

    Add it to TEMPLATES in settings.py:

    TEMPLATES = [{
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'OPTIONS': {
            'environment': 'ufo.jinja.Environment',
        }
    }]
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.install_gettext_translations(django.utils.translation)
        # self.add_extension(LanguageExtension)

        # Populate context with Model classes
        self.globals.update({m.__name__: m for m in apps.all_models['ufo'].values()})

        self.globals.update({
            "plural": utils.templatetags.utils.plural,
            'humanize': django.contrib.humanize.templatetags.humanize,
            'static': django.templatetags.static.static,
            'Count': django.db.models.Count,
            'Q': django.db.models.Q,
            'settings': django.conf.settings,
            'now': pendulum.now,

            'int16': int16,
            'version': ufo.__version__,
            # 'url': reverse,
        })


class LanguageExtension(jinja2.ext.Extension):
    tags = {'language'}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        # Parse the language code argument
        args = [parser.parse_expression()]
        # Parse everything between the start and end tag:
        body = parser.parse_statements(['name:endlanguage'], drop_needle=True)
        # Call the _switch_language method with the given language code and body
        return jinja2.ext.nodes.CallBlock(self.call_method('_switch_language', args), [], [], body).set_lineno(lineno)

    def _switch_language(self, language_code, caller):
        with django.utils.translation.override(language_code):
            # Temporarily override the active language and render the body
            output = caller()
        return output


async def render(request, template_name, context=None) -> str:
    """
    This function is mostly a copy of django.template.backends.jinja2.Template.render().

    It expects that backend with 'NAME': 'jinja2_async' exists in settings.TEMPLATES.
    """
    engine = django.template.engines['jinja2_async']

    if context is None:
        context = {}
    context["request"] = request
    context["csrf_input"] = csrf_input_lazy(request)
    context["csrf_token"] = csrf_token_lazy(request)
    for context_processor in engine.template_context_processors:
        context.update(context_processor(request))

    return await engine.env.get_template(template_name).render_async(context)
    # return HttpResponse(content, content_type, status)

