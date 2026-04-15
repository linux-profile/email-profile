"""Lazy IMAP search bound to a mailbox."""

from __future__ import annotations

import imaplib
import logging
from collections.abc import Iterator
from typing import TYPE_CHECKING, Optional

from email_profile._internal import _build_serializer, _state
from email_profile.eml import EmailSerializer
from email_profile.query import Q, QueryLike, _q

if TYPE_CHECKING:
    from email_profile.mailbox import MailBox

logger = logging.getLogger(__name__)


class Where:
    """Lazy IMAP search; runs on iterate, list, count or exists."""

    CHUNK_SIZE = 100

    def __init__(
        self,
        client: imaplib.IMAP4_SSL,
        mailbox: MailBox,
        query: Optional[QueryLike] = None,
    ) -> None:
        self._client = client
        self._mailbox = mailbox
        self._q = _q(query) if query is not None else Q.all()

    def _uids(self) -> list[str]:
        _state(self._client.select(self._mailbox.name))

        data = _state(self._client.uid("search", None, self._q.mount()))

        if not data or not data[0]:
            return []

        return data[0].decode().split()

    def count(self) -> int:
        """How many messages match — no body fetched."""
        return len(self._uids())

    def exists(self) -> bool:
        """True if at least one message matches."""
        return self.count() > 0

    def uids(self) -> list[str]:
        """Matching IMAP UIDs — no body fetched."""
        return self._uids()

    def iter_messages(self) -> Iterator[EmailSerializer]:
        """Stream matching messages, fetched in chunks."""
        uids = self._uids()

        for start in range(0, len(uids), self.CHUNK_SIZE):
            group = uids[start : start + self.CHUNK_SIZE]
            if not group:
                continue

            messages = _state(
                self._client.uid("fetch", ",".join(group), "(RFC822)")
            )

            logger.info(
                "Fetched %d/%d messages from %s",
                min(start + self.CHUNK_SIZE, len(uids)),
                len(uids),
                self._mailbox.name,
            )

            for entry in messages:
                if not isinstance(entry, tuple):
                    continue

                raw_uid, raw_message = entry

                try:
                    yield _build_serializer(
                        raw_uid=raw_uid,
                        raw_message=raw_message,
                        mailbox=self._mailbox.name,
                    )
                except Exception:
                    logger.exception("Failed to parse message")
                    continue

    def __iter__(self) -> Iterator[EmailSerializer]:
        return self.iter_messages()

    def list_messages(self) -> list[EmailSerializer]:
        """Materialize all matching messages."""
        return list(self.iter_messages())

    def first(self) -> Optional[EmailSerializer]:
        """First match, or None."""
        return next(iter(self.iter_messages()), None)

    def execute(self) -> list[EmailSerializer]:
        """Alias for list_messages."""
        return self.list_messages()

    def __repr__(self) -> str:
        return (
            f"Where(mailbox={self._mailbox.name!r}, query={self._q.mount()!r})"
        )
