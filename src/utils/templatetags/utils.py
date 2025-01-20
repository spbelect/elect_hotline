import re
import os
import time
import datetime

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


r_pat = re.compile('(\d+),(\d+)')
@register.filter
def get_range(val):
    if isinstance(val, int):
        return range(val)
    elif isinstance(val, (str, unicode)):
        _re = r_pat.match(val)
        if _re:
            return range(int(_re.group(1)),int(_re.group(2)))
    return ''

@register.filter
def get(dict, key):    
    return dict[key]


@register.filter
def timestamp(value):
    return time.mktime(value.timetuple())


@register.filter
def fromtimestamp(timestamp):
    try:
        #assume, that timestamp is given in seconds with decimal point
        ts = int(timestamp)
    except ValueError:
        return None
    return datetime.datetime.fromtimestamp(ts)

register.filter(fromtimestamp)


@register.filter
def filename(value):
    return os.path.basename(value.file.name)



def plural(count: int, variants: list[str]) -> str:
    """
    Returns singular or plural text form of count, picking one from list.
    Provided list of variants should have 3 strings: for 1, 2-4, 5-11 plural
    forms.

    >>> plural(1, ['яблоко', 'яблока', 'яблок'])
    'яблоко'
    >>> plural(3, ['яблоко', 'яблока', 'яблок'])
    'яблока'
    >>> plural(11, ['яблоко', 'яблока', 'яблок'])
    'яблок'
    """
    first, second, third = variants

    if count % 100 == 11:
        return third
    if count % 10 == 1:
        return first
    if count % 10 in (2, 3, 4):
        return second
    return third
