import anymail.signals
import anymail.message

from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.core.mail.backends.base import BaseEmailBackend
# from email.utils import parseaddr
from loguru import logger

from . import metrics


@receiver(anymail.signals.post_send)
def email_post_send_handler(
    sender: BaseEmailBackend,
    message: EmailMessage,

    # AnymailStatus has fileds:
    # * message_id
    # * status
    #   - Set of ANYMAIL_STATUSES across all recipients, or None if not yet sent to ESP
    # * recipients: dict[str, AnymailRecipientStatus]
    #   - Per-recipient statuses: { address -> status, ... }
    # * esp_response
    status: anymail.message.AnymailStatus,

    # Email Service Provider name
    esp_name: str,

    **kwargs
):
    """
    After sending email, update prometheus counter.
    """
    # Each recipient's address is a dictionary key in status.recipients
    for address in status.recipients:
        metrics.emails_sent.labels(destination=address).inc()
        logger.info(f'Email sent to {address}')
