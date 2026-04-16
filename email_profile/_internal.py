"""Helpers shared across modules. Not part of the public API."""

from __future__ import annotations

from email_profile.clients.imap.protocol import EmailParser, ImapFetch
from email_profile.core.status import Status
from email_profile.serializers.email import EmailSerializer


def _state(context: tuple) -> list:
    """Validate IMAP response status and return the payload."""
    Status.validate_status(context[0], payload=context[1])
    return context[1]


def _build_serializer(
    raw_uid: bytes, raw_message: bytes, mailbox: str
) -> EmailSerializer:
    uid = ImapFetch((raw_uid, b"")).uid()

    parsed = EmailParser(raw_message)

    return EmailSerializer.from_raw(
        uid=uid or "0",
        mailbox=mailbox,
        raw=raw_message,
        message_id=parsed.message_id(),
        date=parsed.date(),
        from_=parsed.from_(),
        to_=parsed.to(),
    )
