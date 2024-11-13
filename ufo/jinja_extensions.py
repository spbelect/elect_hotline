import django.utils.translation
from jinja2.ext import Extension, nodes


class LanguageExtension(Extension):
    tags = {'language'}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        # Parse the language code argument
        args = [parser.parse_expression()]
        # Parse everything between the start and end tag:
        body = parser.parse_statements(['name:endlanguage'], drop_needle=True)
        # Call the _switch_language method with the given language code and body
        return nodes.CallBlock(self.call_method('_switch_language', args), [], [], body).set_lineno(lineno)

    def _switch_language(self, language_code, caller):
        with django.utils.translation.override(language_code):
            # Temporarily override the active language and render the body
            output = caller()
        return output
