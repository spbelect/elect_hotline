# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import collections
from contextlib import contextmanager
from copy import copy
from functools import wraps
from time import perf_counter, sleep


def retry_kwarg(func):
    """
    Decoreator adds optional 'retry' kwarg to function. Then if 'retry' kwarg will be given
    positive integer on function call and it raised exception - function will be called again
    that many times until it does not raise exception.
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        num_retries_left = kwargs.pop('retry', 0)
        while True:
            try:
                return func(*args, **kwargs)
            except:
                if num_retries_left > 0:
                    num_retries_left -= 1
                    sleep(1)
                else:
                    raise
    return wrapped


def typed_setdefault_recurse(target, defaultdict):
    modified = False
    for key, val in defaultdict.items():
        if key not in target or type(target[key]) != type(val):
            modified = True
            target[key] = copy(val)
        elif isinstance(val, collections.Mapping):
            if typed_setdefault_recurse(target[key], val) is True:
                modified = True
    return modified


def update(target, source):
    """
    Recursively update dictionary.
    """
    for key, value in source.items():
        if isinstance(value, collections.Mapping):
            target[key] = update(target.get(key, {}), value)
        else:
            target[key] = source[key]
    return target


def partial_method(f, *fargs, **fkwargs):
    def wrapper(self, *args, **kwargs):
        kwargs.update(fkwargs)
        return f(self, *(args + fargs), **kwargs)
    return wrapper


def pairs(iterable):
    ''' ABCDE -> (A,B), (C,D), E '''
    for i in range(len(iterable) / 2):
        yield iterable[i * 2], iterable[i * 2 + 1]
    if len(iterable) % 2:
        yield iterable[-1]


def sliced(iterable, slice_len):
    for i in xrange(0, len(iterable), slice_len):
        yield iterable[slice(i, i + slice_len)]


def utf8_str(s):
    if isinstance(s, unicode):
        return s.encode('utf-8')
    return s


enum_list = lambda l: [(n, val) for n, val in enumerate(l,1)]


key = lambda map, val: dict((val,key) for key, val in map.items())[val]


@contextmanager
def tmit():
    """
    Print elapsed time for context expression.
    Usage:
    >>> with tmit():
    >>>     my_function()  # some expresion to measure

    """
    t1 = perf_counter()
    yield
    t2 = perf_counter()
    print('%0.2f seconds elapsed' % (t2 - t1))


MEMOIZE_CACHE = {}


def memoize(func):
    def wrapped(*args, **kwargs):
        global MEMOIZE_CACHE
        _key = (func, tuple(args), tuple(sorted(kwargs.items())))
        if _key in MEMOIZE_CACHE:
            return MEMOIZE_CACHE[_key]
        result = func(*args, **kwargs)
        MEMOIZE_CACHE[_key] = result
        return result
    return wrapped
