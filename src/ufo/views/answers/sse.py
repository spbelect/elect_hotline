import asyncio
import json

import django
import sentry_sdk

from datetime import datetime, date, time, timezone, timedelta
from typing import Literal, Any, Optional, Annotated, AsyncGenerator
from collections.abc import Iterator

from django.conf import settings
from django.utils.translation import gettext as _
from loguru import logger
from pendulum import now

from ufo.models import Answer, int16, Region, WebsiteUser

import ufo.jinja

from . import stream


async def worker(
    request,
    filters: stream.Filters,
    time_created__gt: datetime
) -> AsyncGenerator[str, None]:
    """
    SSE Worker. Used in /answers/stream/sse http handler.

    Wraps one of the poll_database(), redis_pubsub() or postgres_pubsub(), depending
    on settings.ANSWERS_SSE_ENGINE variable.

    Wrapped workers yield SSE string for each answer:
        event: answer
        data: <li>...</li>

    """

    try:
        # We must send start event immediately so that js EventSource will change
        # state from "connecting" to "open". Otherwise frontend will not know
        # that connection succeeded until the first new answer arrives.
        yield f"event: start\ndata: null\n\n"

        match settings.ANSWERS_SSE_ENGINE:
            case 'views.answers.sse.poll_database':
                engine = poll_database
            case 'views.answers.sse.redis_pubsub':
                engine = redis_pubsub
            case 'views.answers.sse.postgres_pubsub':
                engine = postgres_pubsub

        async for result in engine(request, filters, time_created__gt):
            yield result
    except asyncio.CancelledError:
        # logger.debug('Stream end')
        raise
    except Exception as err:
        logger.exception(err)
        sentry_sdk.capture_exception(err)
        raise


async def poll_database(request, filters, time_created__gt) -> AsyncGenerator[str, None]:
    """
    Infinite loop every few seconds queries database for new answers and yields SSE
    string for each answer:
        event: answer
        data: <li>...</li>

    Pros:
    * Supports any database including SQLite.
    * Doesn't require any additional infrastructure.

    Cons:
    * Polling might overload database when many users listen to
      the stream simultaneously.

    In production, it is better to use redis or postgres pubsub instead.
    """

    answers = filters().order_by('time_created')

    while True:
        # Perform simple database polling for new answers every few seconds.
        async for answer in answers.filter(time_created__gt=time_created__gt):
            html = await ufo.jinja.render(request, 'views/answers/_answer.html', dict(
                answer = answer
            ))
            time_created__gt = answer.time_created

            # logger.debug(f'{answer}, {answer.time_created} > {time_created__gt}')
            yield f"event: answer\ndata: {html.replace('\n', '')}\n\n"

        await asyncio.sleep(settings.ANSWERS_SSE_POLL_DB_DELAY)


async def redis_pubsub(request, filters, time_created__gt) -> AsyncGenerator[str, None]:

    raise NotImplementedError('WIP')

##    Based on https://github.com/LucidDan/htmx-notifications/blob/main/demo/urls.py
#     import redis.asyncio
#     redis = redis.asyncio.from_url(settings.REDIS_URL)
#
#     async with redis.pubsub() as pubsub:
#         await pubsub.subscribe('answers')
#         while True:
#             msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=None)
#             if msg is None:
#                 continue
#             data = json.loads(msg["data"])


async def postgres_pubsub(request, filters, time_created__gt) -> AsyncGenerator[str, None]:

    raise NotImplementedError('WIP')
