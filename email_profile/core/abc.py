"""Abstract base classes for IMAP, SMTP and Storage backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from email.message import EmailMessage
from typing import Optional, Union

from email_profile.serializers.email import EmailSerializer


class StorageABC(ABC):
    """Contract for a message-persistence backend."""

    @abstractmethod
    def save(self, serializer: EmailSerializer) -> object: ...

    @abstractmethod
    def save_many(
        self,
        serializers: Iterable[EmailSerializer],
        *,
        batch_size: Optional[int] = None,
    ) -> int: ...

    @abstractmethod
    def messages(
        self, mailbox: Optional[str] = None
    ) -> Iterator[EmailSerializer]: ...

    @abstractmethod
    def existing_ids(self, mailbox: Optional[str] = None) -> set[str]: ...

    @abstractmethod
    def existing_uids(self, mailbox: str) -> set[str]: ...

    @abstractmethod
    def dispose(self) -> None: ...


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
