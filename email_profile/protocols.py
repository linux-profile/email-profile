"""Public Protocol contracts for swappable backends.

These are PEP 544 ``Protocol`` types: any class that implements the listed
methods satisfies the protocol — no inheritance required.

Use them in your own code to type-check or to build a custom backend
(e.g. Postgres, Redis, in-memory) that the rest of the library accepts
transparently.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Optional, Protocol, runtime_checkable

from email_profile.eml import EmailSerializer


@runtime_checkable
class StorageProtocol(Protocol):
    """Minimum contract for a message-persistence backend.

    Any object exposing this surface can be passed to ``Email.restore`` or
    to any helper that takes a storage parameter — including custom
    in-memory, S3, Postgres, etc. backends.
    """

    def save(self, serializer: EmailSerializer) -> object:
        """Persist a single message and return any backend-specific row."""
        ...

    def save_many(
        self,
        serializers: Iterable[EmailSerializer],
        *,
        batch_size: Optional[int] = None,
    ) -> int:
        """Persist many messages in one or more transactions; return count."""
        ...

    def messages(
        self, mailbox: Optional[str] = None
    ) -> Iterator[EmailSerializer]:
        """Stream persisted messages back, optionally filtered by mailbox."""
        ...

    def existing_ids(self, mailbox: Optional[str] = None) -> set[str]:
        """Return Message-IDs already stored — enables resumable backups."""
        ...

    def existing_uids(self, mailbox: str) -> set[str]:
        """Return persisted IMAP UIDs for one mailbox."""
        ...

    def dispose(self) -> None:
        """Release any underlying resources (connection pools, files, ...)."""
        ...
