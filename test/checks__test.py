import django.test
import pytest

from django.core.management import call_command, CommandError


class SystemcheckTestCase(django.test.TestCase):
    def test_systemcheck(self):
        with pytest.raises(CommandError):
            call_command('check', *['--deploy'], **{})
