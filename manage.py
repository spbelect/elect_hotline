#!/usr/bin/env python
import os
import sys
from traceback import format_exc, format_tb
from environ import ImproperlyConfigured

if __name__ == "__main__":
    if os.path.exists('settings_local.py'):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_local")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    try:
        execute_from_command_line(sys.argv)
    except ImproperlyConfigured as e:
        print('\n'.join(format_exc().split('\n')[-10:]), end='')
        print('NOTE: You can try to edit environment variables in env-local file.',)
        
