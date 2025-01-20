from __future__ import absolute_import

import logging

from django.conf import settings


def check_redis(logger=None):
    from redis import Redis, ConnectionError

    if not logger:
        logger = logging.getLogger('utils.redis')

    redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    key = 'aeriuha9gyaaoguba408yha34'

    try:
        redis.set(key, '1')
    except ConnectionError as e:
        logger.error("Failed to connect to redis using REDIS_HOST and REDIS_PORT settings.")
        raise

    assert(redis.get(key) == '1')

    redis.delete(key)
