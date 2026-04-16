"""Helpers shared across modules. Not part of the public API."""

from __future__ import annotations

from email_profile.clients.imap.parser import FetchParser
from email_profile.core.status import Status
from email_profile.serializers.email import Message


def _state(context: tuple) -> list:
    """Validate IMAP response status and return the payload."""
    Status.validate_status(context[0], payload=context[1])
    return context[1]


def _build_serializer(
    raw_uid: bytes, raw_message: bytes, mailbox: str
) -> Message:
    uid = FetchParser((raw_uid, b""))._parse_uid()

    return Message.from_raw(
        uid=uid or "0",
        mailbox=mailbox,
        raw=raw_message,
    )
