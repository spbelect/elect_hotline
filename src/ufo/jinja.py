from django.apps import apps
from django.conf import settings

import django.contrib.humanize.templatetags.humanize
import django.templatetags.static
import django.utils.translation
import jinja2.ext

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

            'settings': django.conf.settings,

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
