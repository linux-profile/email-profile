"""Lazy IMAP search bound to a mailbox."""

from __future__ import annotations

import imaplib
import logging
from collections.abc import Iterator
from typing import TYPE_CHECKING, Callable, Literal, Optional

from email_profile._internal import _build_serializer, _state
from email_profile.clients.imap.query import Q, QueryLike, _q
from email_profile.retry import with_retry
from email_profile.serializers.email import EmailSerializer

if TYPE_CHECKING:
    from email_profile.clients.imap.mailbox import MailBox

logger = logging.getLogger(__name__)

FetchMode = Literal["full", "text", "headers"]

_FETCH_SPECS: dict[str, str] = {
    "full": "(RFC822)",
    "text": "(BODY.PEEK[HEADER] BODY.PEEK[TEXT])",
    "headers": "(BODY.PEEK[HEADER])",
}


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
        self._cached_uids: Optional[list[str]] = None

    def _uids(self) -> list[str]:
        if self._cached_uids is not None:
            return self._cached_uids

        from email_profile.clients.imap.mailbox import _quote

        _state(self._client.select(_quote(self._mailbox.name)))

        data = _state(self._client.uid("search", None, self._q.mount()))

        if not data or not data[0]:
            self._cached_uids = []
            return self._cached_uids

        self._cached_uids = data[0].decode().split()
        return self._cached_uids

    def clear_cache(self) -> Where:
        """Drop cached UIDs so the next call hits IMAP again."""
        self._cached_uids = None
        return self

    def count(self) -> int:
        """How many messages match — no body fetched."""
        return len(self._uids())

    def exists(self) -> bool:
        """True if at least one message matches."""
        return self.count() > 0

    def uids(self) -> list[str]:
        """Matching IMAP UIDs — no body fetched."""
        return list(self._uids())

    def messages(
        self,
        *,
        mode: FetchMode = "full",
        chunk_size: Optional[int] = None,
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> Iterator[EmailSerializer]:
        """Stream matching messages, fetched in chunks. Wrap in ``list()``
        if you need a materialized list.

        ``mode``:
            - ``"full"``  — RFC822 with attachments (default).
            - ``"text"``  — headers + body, no attachments (~50x lighter).
            - ``"headers"`` — headers only (cheapest).

        ``chunk_size`` overrides ``CHUNK_SIZE`` for this call. Larger values
        ride faster servers; smaller ones survive flaky links.

        ``on_progress`` is called with ``(done, total)`` after each chunk.
        """

        spec = _FETCH_SPECS.get(mode)
        if spec is None:
            raise ValueError(
                f"Unknown fetch mode {mode!r}. Use one of: {sorted(_FETCH_SPECS)}"
            )

        size = chunk_size or self.CHUNK_SIZE
        uids = self._uids()
        total = len(uids)

        fetch = with_retry()(self._fetch_chunk)

        for start in range(0, total, size):
            group = uids[start : start + size]
            if not group:
                continue

            messages = fetch(group, spec)

            done = min(start + size, total)
            logger.info(
                "Fetched %d/%d messages from %s (mode=%s)",
                done,
                total,
                self._mailbox.name,
                mode,
            )
            if on_progress is not None:
                on_progress(done, total)

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
                    uid_text = (
                        raw_uid.decode(errors="replace") if raw_uid else "?"
                    )
                    logger.exception(
                        "Failed to parse message uid=%s mailbox=%s",
                        uid_text,
                        self._mailbox.name,
                    )
                    continue

    def _fetch_chunk(self, group: list[str], spec: str) -> list:
        return _state(self._client.uid("fetch", ",".join(group), spec))

    def __repr__(self) -> str:
        return (
            f"Where(mailbox={self._mailbox.name!r}, query={self._q.mount()!r})"
        )
