"""Minimal serializer for raw email storage."""

from __future__ import annotations

from typing import Union

from pydantic import BaseModel, ConfigDict, field_validator


class RawSerializer(BaseModel):
    """Minimum data contract for any storage backend.

    ``file`` stores the raw RFC822 bytes verbatim so binary attachments
    and non-UTF8 bodies round-trip without loss. ``str`` input is accepted
    for backward compatibility and encoded as latin-1 (byte-preserving).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    message_id: str
    uid: str
    mailbox: str
    flags: str = ""
    file: bytes

    @field_validator("file", mode="before")
    @classmethod
    def _coerce_file(
        cls, value: Union[bytes, bytearray, memoryview, str]
    ) -> bytes:
        if isinstance(value, (bytes, bytearray, memoryview)):
            return bytes(value)
        if isinstance(value, str):
            return value.encode("latin-1", errors="replace")
        raise TypeError(
            f"file must be bytes or str, got {type(value).__name__}"
        )
