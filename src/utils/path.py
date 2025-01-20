import os
from os.path import join, isdir


def makedirs(*parts):
    absdir = join(*parts)
    try:
        os.makedirs(absdir)
    except os.error:
        if not isdir(absdir):
            raise
    return absdir


def abs_listdir(path):
    return [join(path, filename) for filename in os.listdir(path)]
