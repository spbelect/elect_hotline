from __future__ import absolute_import

import os
import logging
from shutil import rmtree
from subprocess import Popen

import django.conf

from .basic import memoize


def sh(*cmd, **kwargs):
    return Popen(' '.join(cmd), shell=True, close_fds=True, **kwargs)


def sh_wait(*cmd, **kwargs):
    return sh(*cmd, **kwargs).wait()


@memoize
def get_bin(*aliases):
    for name in aliases:
        if sh_wait('which', name, stdout=open('/dev/null'), stderr=open('/dev/null')) == 0:
            return name
    raise Exception('%s not found' % ' or '.join(aliases))


def extract(archive_path, dst_dir):
    p7z = get_bin('7z', '7za')

    # 'e': extract. '-y': force
    return sh_wait(p7z, 'e -y -o%s %s' % (dst_dir, archive_path), stdout=open('/dev/null'))


def compress(archive_path, src):
    p7z = get_bin('7z', '7za')

    # 'a': compress.
    return sh_wait(p7z, 'a %s %s' % (archive_path, src), stdout=open('/dev/null'))


def mk_config(settings=django.conf.settings):
    from django.template import Context, Template
    with open(settings.SPHINX['CONFIG_TEMPLATE']) as f:
        template = Template(f.read())
    config = template.render(Context({'settings': settings}))
    with open(settings.SPHINX['CONFIG_PATH'], 'w+') as f:
        f.write(config)
    return settings.SPHINX['CONFIG_PATH']


def sphinx_mk_dirs(settings=django.conf.settings):
    for path in ['RUN_PATH', 'LOG_PATH', 'DB_PATH']:
        if not os.path.exists(settings.SPHINX[path]):
            os.makedirs(settings.SPHINX[path])


def sphinx_rm_dirs(settings=django.conf.settings):
    for path in ['RUN_PATH', 'LOG_PATH', 'DB_PATH']:
        if os.path.exists(settings.SPHINX[path]):
            rmtree(settings.SPHINX[path])


def indexer(*args, **kwargs):
    indexer = get_bin('sphinx-indexer', 'indexer')
    settings = kwargs.pop('settings', django.conf.settings)
    sphinx_mk_dirs(settings)
    cmd = (indexer, '--config', mk_config(settings), '--rotate')
    dump_rows_path = getattr(settings, 'SPHINX_INDEXER_DUMP_PATH', None)
    if dump_rows_path:
        cmd += ('--dump-rows %s' % dump_rows_path,)
    print_queries = getattr(settings, 'SPHINX_INDEXER_PRINT_QUERIES', False)
    if print_queries:
        cmd += ('--print-queries',)
    cmd += args
    logging.debug('running %s' % ' '.join(cmd))
    sh_wait(*cmd)


def searchd(*args, **kwargs):
    searchd = get_bin('sphinx-searchd', 'searchd')
    settings = kwargs.pop('settings', django.conf.settings)
    sphinx_mk_dirs(settings)
    # NOTE: close_fds=True to prevent sphinx takeover of listening tcp ports of parent
    # process (django server) after death of parent. Otherwise subsequent django server
    # startup will fail because TCP ports it will want to listen are unavailable.
    return sh(searchd, '--config', mk_config(settings), *args)
