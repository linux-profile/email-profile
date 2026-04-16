"""IMAP fetch spec builder.

Composable fetch specifications for IMAP FETCH commands::

    F.rfc822()                          # full email
    F.flags()                           # just flags
    F.header("Message-ID")             # single header
    F.headers("From", "Subject")       # multiple headers
    F.body_text()                       # headers + body, no attachments
    F.rfc822() + F.flags()             # combine specs
"""

from __future__ import annotations

import imaplib
from collections.abc import Iterator
from typing import TYPE_CHECKING

from email_profile.clients.imap.parser import FetchParser
from email_profile.core.status import Status
from email_profile.retry import with_retry

if TYPE_CHECKING:
    from email_profile.clients.imap.mailbox import MailBox


class F:
    """Composable IMAP fetch specification."""

    __slots__ = ("_spec",)

    def __init__(self, spec: str) -> None:
        self._spec = spec

    def mount(self) -> str:
        return self._spec

    def __add__(self, other: F) -> F:
        left = self._spec.strip("()")
        right = other._spec.strip("()")
        return F(f"({left} {right})")

    def __repr__(self) -> str:
        return f"F({self._spec!r})"

    @staticmethod
    def rfc822() -> F:
        return F("(RFC822)")

    @staticmethod
    def flags() -> F:
        return F("(FLAGS)")

    @staticmethod
    def all_headers() -> F:
        return F("(BODY.PEEK[HEADER])")

    @staticmethod
    def header(name: str) -> F:
        return F(f"(BODY.PEEK[HEADER.FIELDS ({name.upper()})])")

    @staticmethod
    def headers(*names: str) -> F:
        fields = " ".join(n.upper() for n in names)
        return F(f"(BODY.PEEK[HEADER.FIELDS ({fields})])")

    @staticmethod
    def body_text() -> F:
        return F("(BODY.PEEK[HEADER] BODY.PEEK[TEXT])")

    @staticmethod
    def body_peek() -> F:
        return F("(BODY.PEEK[])")

    @staticmethod
    def envelope() -> F:
        return F("(ENVELOPE)")

    @staticmethod
    def size() -> F:
        return F("(RFC822.SIZE)")


class Fetch:
    """Execute UID FETCH in chunks and yield parsed entries."""

    CHUNK_SIZE = 100

    def __init__(
        self,
        *,
        client: imaplib.IMAP4_SSL,
        mailbox: MailBox,
        spec: F,
        chunk_size: int = CHUNK_SIZE,
    ) -> None:
        self._client = client
        self._mailbox = mailbox
        self._spec = spec.mount()
        self._chunk_size = chunk_size

    def _select(self) -> None:
        from email_profile.clients.imap.mailbox import _quote

        Status.state(self._client.select(_quote(self._mailbox.name)))

    def _fetch_chunk(self, group: list[str]) -> list:
        return Status.state(
            self._client.uid("fetch", ",".join(group), self._spec)
        )

    def chunks(self, uids: list[str]) -> Iterator[list]:
        """Yield raw IMAP response lists per chunk."""
        self._select()
        fetch = with_retry()(self._fetch_chunk)

        for start in range(0, len(uids), self._chunk_size):
            group = uids[start : start + self._chunk_size]
            yield fetch(group)

    def parsed(self, uids: list[str]) -> Iterator[FetchParser]:
        """Yield parsed entries with resolved flags."""
        for fetched in self.chunks(uids):
            yield from FetchParser.iter_entries(fetched)

    @staticmethod
    def fetch_message_ids(
        client: object, uids: list[str], chunk_size: int = 500
    ) -> dict[str, str]:
        """Fetch Message-IDs from server. Returns {uid: message_id}."""

        result: dict[str, str] = {}

        for start in range(0, len(uids), chunk_size):
            group = uids[start : start + chunk_size]

            status, fetched = client.uid(
                "fetch",
                ",".join(group),
                "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])",
            )
            if status != "OK":
                continue

            for entry in fetched:
                if not FetchParser.is_valid(entry):
                    continue

                d = FetchParser(entry)
                uid = d._parse_uid()
                msg_id = d._parse_message_id()

                if uid and msg_id:
                    result[uid] = msg_id

        return result
