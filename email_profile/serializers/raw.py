"""Minimal serializer for raw email storage."""

from __future__ import annotations

from pydantic import BaseModel


class RawSerializer(BaseModel):
    """Minimum data contract for any storage backend."""

    message_id: str
    uid: str
    mailbox: str
    flags: str = ""
    file: str
