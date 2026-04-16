"""Helpers shared across modules. Not part of the public API."""

from __future__ import annotations

import re
from email import message_from_bytes
from email.utils import parseaddr, parsedate_to_datetime

from email_profile.core.status import Status
from email_profile.serializers.email import EmailSerializer

_UID_RE = re.compile(rb"UID (\d+)")


def _state(context: tuple) -> list:
    """Validate IMAP response status and return the payload."""
    Status.validate_status(context[0], payload=context[1])
    return context[1]


def _build_serializer(
    raw_uid: bytes, raw_message: bytes, mailbox: str
) -> EmailSerializer:
    content = message_from_bytes(raw_message)

    raw_date = content.get("Date")
    parsed_date = None
    if raw_date:
        try:
            parsed_date = parsedate_to_datetime(raw_date)
        except (TypeError, ValueError):
            parsed_date = None

    match = _UID_RE.search(raw_uid)
    uid = match.group(1).decode() if match else raw_uid.decode().split()[0]

    return EmailSerializer.from_raw(
        uid=uid,
        mailbox=mailbox,
        raw=raw_message,
        message_id=content.get("Message-ID"),
        date=parsed_date,
        from_=parseaddr(content.get("From", ""))[1] or None,
        to_=parseaddr(content.get("To", ""))[1] or None,
    )
