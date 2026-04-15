"""A single IMAP mailbox."""

from __future__ import annotations

import imaplib
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Union

from email_profile._internal import _state
from email_profile.query import Query, QueryLike
from email_profile.retry import with_retry
from email_profile.searches import Where

if TYPE_CHECKING:
    from email_profile.eml import EmailSerializer


MessageLike = Union["EmailSerializer", bytes, str]


@dataclass(frozen=True)
class AppendedUID:
    """Result of a successful IMAP APPEND when the server supports UIDPLUS."""

    uidvalidity: int
    uid: int


_APPENDUID_RE = re.compile(rb"APPENDUID (\d+) (\d+)")


def _parse_append_uid(payload: object) -> Optional[AppendedUID]:
    candidates = payload if isinstance(payload, list) else [payload]
    for chunk in candidates:
        if isinstance(chunk, bytes):
            match = _APPENDUID_RE.search(chunk)
            if match:
                return AppendedUID(
                    uidvalidity=int(match.group(1)),
                    uid=int(match.group(2)),
                )
    return None


class MailBox:
    """One IMAP mailbox addressed by its server-side name."""

    PATTERN = re.compile(
        r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)'
    )

    def __init__(
        self,
        client: imaplib.IMAP4_SSL,
        name: str,
        delimiter: str = "/",
        flags: Optional[list[str]] = None,
    ) -> None:
        self._client = client
        self.name = name.strip().strip('"')
        self.delimiter = delimiter
        self.flags = flags or []

    @classmethod
    def from_imap_detail(
        cls,
        client: imaplib.IMAP4_SSL,
        detail: bytes,
    ) -> MailBox:
        """Parse one entry from IMAP.list()."""

        match = cls.PATTERN.match(detail.decode("utf-8"))

        if match is None:
            raise ValueError(f"Cannot parse mailbox detail: {detail!r}")

        flags_raw, delimiter, name = match.groups()
        flags = [flag.strip("\\") for flag in flags_raw.split()]

        return cls(client=client, name=name, delimiter=delimiter, flags=flags)

    def where(self, query: Optional[QueryLike] = None, **kwargs) -> Where:
        """Build a lazy search; pass a Query/Q/string OR filter kwargs."""

        if query is not None and kwargs:
            raise TypeError(
                "Pass either a Query/Q expression OR kwargs, not both."
            )

        if query is None:
            query = Query(**kwargs) if kwargs else Query()

        return Where(client=self._client, mailbox=self, query=query)

    def append(
        self,
        message: MessageLike,
        flags: str = "",
        date: Optional[datetime] = None,
    ) -> Optional[AppendedUID]:
        """Upload one message into this mailbox via IMAP APPEND.

        Returns the new ``AppendedUID`` when the server supports UIDPLUS
        (RFC 4315). Returns ``None`` otherwise — the message is still saved.
        """

        from email_profile.eml import EmailSerializer

        if isinstance(message, EmailSerializer):
            raw = message.file.encode("utf-8")
            if date is None:
                date = message.date
        elif isinstance(message, str):
            raw = message.encode("utf-8")
        elif isinstance(message, bytes):
            raw = message
        else:
            raise TypeError(
                "append expects EmailSerializer, bytes or str — "
                f"got {type(message).__name__}"
            )

        date_time = imaplib.Time2Internaldate(
            date.timestamp() if date else time.time()
        )

        do_append = with_retry()(self._client.append)
        status, payload = do_append(self.name, flags, date_time, raw)
        _state((status, payload))
        return _parse_append_uid(payload)

    def __repr__(self) -> str:
        return f"MailBox(name={self.name!r}, flags={self.flags})"
