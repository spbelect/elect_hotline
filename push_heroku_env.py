#!/usr/bin/env python

import os
import re
from os.path import abspath, dirname, join, exists
from subprocess import check_output

import click
from click import Context, confirm, command, option, group, argument

Context.get_usage = Context.get_help  # show full help on error


def sh(cmd):
    return check_output(cmd, shell=True)


def strip(file):
    for line in file.readlines():
        if line.strip() and not line.startswith('#'):
            yield line.strip()
            
@command()
@argument('envfile', type=click.File('r'))
@option('--app', '-a', envvar='HEROKUAPP')
def cli(envfile, app):
    #print(list(strip(envfile)))
    sh(f'heroku config:set --app {app} {" ".join(strip(envfile))}')
    print('Configuration succeeded.')


if __name__ == "__main__":
    cli()
