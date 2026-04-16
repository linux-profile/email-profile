"""Abstract base classes for IMAP, SMTP and Storage backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from email.message import EmailMessage
from typing import Optional, Union

from email_profile.serializers.email import EmailSerializer
from email_profile.serializers.raw import RawSerializer


@dataclass
class SyncResult:
    """Outcome of a mailbox sync operation."""

    mailbox: str
    inserted: int = 0
    updated: int = 0
    deleted: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total_processed(self) -> int:
        return self.inserted + self.updated + self.deleted + self.skipped

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def merge(self, other: SyncResult) -> SyncResult:
        return SyncResult(
            mailbox="*",
            inserted=self.inserted + other.inserted,
            updated=self.updated + other.updated,
            deleted=self.deleted + other.deleted,
            skipped=self.skipped + other.skipped,
            errors=self.errors + other.errors,
        )


class StorageABC(ABC):
    """Contract for a message-persistence backend."""

    @abstractmethod
    def save_raw(self, raw: RawSerializer) -> None:
        """Persist the complete RFC822 source for one email."""
        ...

    @abstractmethod
    def get_raw(self, message_id: str) -> Optional[RawSerializer]:
        """Retrieve the RFC822 source by email id. None if not stored."""
        ...

    @abstractmethod
    def stored_ids(self) -> set[str]: ...

    @abstractmethod
    def stored_uids(self, mailbox: str) -> set[str]: ...


class ImapClientABC(ABC):
    """Contract for an IMAP connection manager."""

    server: str
    user: str
    password: str
    port: int
    ssl: bool

    @property
    @abstractmethod
    def is_connected(self) -> bool: ...

    @abstractmethod
    def connect(self) -> ImapClientABC: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def noop(self) -> None: ...

    @abstractmethod
    def require(self) -> None: ...


class SmtpClientABC(ABC):
    """Contract for an SMTP connection manager."""

    @property
    @abstractmethod
    def is_connected(self) -> bool: ...

    @abstractmethod
    def connect(self) -> SmtpClientABC: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def send(self, message: EmailMessage) -> None: ...


class SenderABC(ABC):
    """Contract for outgoing mail (send, reply, forward)."""

    @abstractmethod
    def send(
        self,
        to: Union[str, list[str]],
        subject: str,
        body: str = "",
        *,
        save_to_sent: bool = True,
    ) -> None: ...

    @abstractmethod
    def send_message(
        self,
        message: EmailMessage,
        *,
        save_to_sent: bool = True,
    ) -> None: ...

    @abstractmethod
    def reply(
        self,
        original: EmailSerializer,
        body: str = "",
        *,
        save_to_sent: bool = True,
    ) -> None: ...

    @abstractmethod
    def forward(
        self,
        original: EmailSerializer,
        to: Union[str, list[str]],
        body: str = "",
        *,
        save_to_sent: bool = True,
    ) -> None: ...
