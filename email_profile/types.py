"""Public value types used across the package."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IMAPHost:
    """The IMAP host + port + ssl flag for an account."""

    host: str
    port: int = 993
    ssl: bool = True


@dataclass(frozen=True)
class AppendedUID:
    """Result of a successful IMAP APPEND when the server supports UIDPLUS."""

    uidvalidity: int
    uid: int
