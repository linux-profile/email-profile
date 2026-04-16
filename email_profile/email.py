# ruff: noqa: ARG001
"""IMAP client (high-level entry point)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from email_profile.clients.imap.client import ImapClient
from email_profile.clients.imap.folders import FolderAccess
from email_profile.clients.imap.queries import QueryShortcuts
from email_profile.clients.imap.restore import Restore
from email_profile.clients.imap.sync import Sync
from email_profile.clients.imap.where import Where
from email_profile.clients.smtp.client import AttachmentLike
from email_profile.clients.smtp.sender import Sender
from email_profile.core.abc import StorageABC, SyncResult
from email_profile.core.credentials import Credentials, EmailFactories
from email_profile.storage.sqlite import StorageSQLite

if TYPE_CHECKING:
    from email.message import EmailMessage

    from email_profile.clients.imap.mailbox import MailBox
    from email_profile.core.types import SMTPHost
    from email_profile.serializers.email import Message


class Email:
    """IMAP + SMTP client. Lazy connect via ``with Email(...) as app:``.

    Constructor overloads::

        Email(user="u@gmail.com", password="pw")          # auto-discover
        Email("u@gmail.com", "pw")                          # same, positional
        Email("imap.gmail.com", "u", "pw")                  # explicit host
        Email(server="...", user="...", password="...")     # full kwargs
        Email()                                              # zero args -> env
    """

    def __init__(
        self,
        server: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 993,
        ssl: bool = True,
        storage: Optional[StorageABC] = None,
    ) -> None:
        connection = self._resolve(server, user, password, port, ssl)

        self._session = ImapClient(
            server=connection.server,
            user=connection.user,
            password=connection.password,
            port=connection.port,
            ssl=connection.ssl,
        )
        self._folders = FolderAccess(self._session)
        self._queries = QueryShortcuts(self._folders)
        self._sync = Sync(self._session)
        self._restore = Restore(self._session)
        self._sender = Sender(self._session, self._folders)
        self._storage = storage

    @property
    def storage(self) -> StorageABC:
        if self._storage is None:
            self._storage = StorageSQLite()
        return self._storage

    @storage.setter
    def storage(self, value: StorageABC) -> None:
        self._storage = value

    @staticmethod
    def _resolve(
        server: Optional[str],
        user: Optional[str],
        password: Optional[str],
        port: int,
        ssl: bool,
    ) -> Credentials:
        if server is None and user is None and password is None:
            return EmailFactories.from_env()

        if password is None and user is not None and server and "@" in server:
            return EmailFactories.from_address(server, user)

        if server is None and user is not None and "@" in user and password:
            return EmailFactories.from_address(user, password)

        if server is None or user is None or password is None:
            raise TypeError(
                "Email() requires (server, user, password), "
                "or (user='you@domain', password=...) for auto-discovery, "
                "or no args (env vars)."
            )

        return Credentials(
            server=server, user=user, password=password, port=port, ssl=ssl
        )

    @property
    def server(self) -> str:
        return self._session.server

    @property
    def user(self) -> str:
        return self._session.user

    @property
    def port(self) -> int:
        return self._session.port

    @property
    def ssl(self) -> bool:
        return self._session.ssl

    @property
    def is_connected(self) -> bool:
        return self._session.is_connected

    @classmethod
    def from_email(cls, address: str, password: str) -> Email:
        """Auto-discover the IMAP host from the address."""
        creds = EmailFactories.from_address(address, password)
        return cls(
            server=creds.server,
            user=creds.user,
            password=creds.password,
            port=creds.port,
            ssl=creds.ssl,
        )

    @classmethod
    def from_env(
        cls,
        server_var: str = "EMAIL_SERVER",
        user_var: str = "EMAIL_USERNAME",
        password_var: str = "EMAIL_PASSWORD",
        load_dotenv: bool = True,
    ) -> Email:
        """Read credentials from env or .env; auto-discover if missing."""
        creds = EmailFactories.from_env(
            server_var=server_var,
            user_var=user_var,
            password_var=password_var,
            load_dotenv=load_dotenv,
        )
        return cls(
            server=creds.server, user=creds.user, password=creds.password
        )

    def connect(self) -> Email:
        self._session.connect()
        return self

    def close(self) -> None:
        self._session.close()

    def noop(self) -> None:
        self._session.noop()

    def mailboxes(self) -> list[str]:
        return self._folders.mailboxes()

    def mailbox(self, name: str) -> MailBox:
        return self._folders.mailbox(name)

    @property
    def inbox(self) -> MailBox:
        return self._folders.inbox

    @property
    def sent(self) -> MailBox:
        return self._folders.sent

    @property
    def spam(self) -> MailBox:
        return self._folders.spam

    @property
    def trash(self) -> MailBox:
        return self._folders.trash

    @property
    def drafts(self) -> MailBox:
        return self._folders.drafts

    @property
    def archive(self) -> MailBox:
        return self._folders.archive

    def unread(self) -> Where:
        return self._queries.unread()

    def recent(self, days: int = 7) -> Where:
        return self._queries.recent(days)

    def search(self, text: str) -> Where:
        return self._queries.search(text)

    def all(self) -> Where:
        return self._queries.all()

    def sync(
        self,
        mailbox: Optional[str] = None,
        max_workers: int = 3,
        skip_duplicates: bool = True,
    ) -> SyncResult:
        """Sync server state into local storage."""
        return self._sync.orchestrate(
            storage=self.storage,
            mailbox=mailbox,
            mailbox_names=self._folders.mailboxes() if not mailbox else None,
            max_workers=max_workers,
            skip_duplicates=skip_duplicates,
        )

    def restore(
        self,
        mailbox: Optional[str] = None,
        storage: Optional[StorageABC] = None,
        skip_duplicates: bool = True,
        max_workers: int = 3,
    ) -> int:
        return self._restore.orchestrate(
            storage=storage or self.storage,
            mailbox=mailbox,
            skip_duplicates=skip_duplicates,
            max_workers=max_workers,
        )

    def smtp_host(self) -> SMTPHost:
        return self._sender.smtp_host()

    def send(
        self,
        to: Union[str, list[str]],
        subject: str,
        body: str = "",
        *,
        html: Optional[str] = None,
        cc: Optional[Union[str, list[str]]] = None,
        bcc: Optional[Union[str, list[str]]] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[list[AttachmentLike]] = None,
        headers: Optional[dict[str, str]] = None,
        save_to_sent: bool = True,
    ) -> None:
        self._sender.send(
            to=to,
            subject=subject,
            body=body,
            html=html,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
            attachments=attachments,
            headers=headers,
            save_to_sent=save_to_sent,
        )

    def send_message(
        self,
        message: EmailMessage,
        *,
        save_to_sent: bool = True,
    ) -> None:
        self._sender.send_message(message, save_to_sent=save_to_sent)

    def reply(
        self,
        original: Message,
        body: str = "",
        *,
        html: Optional[str] = None,
        attachments: Optional[list[AttachmentLike]] = None,
        reply_all: bool = False,
        save_to_sent: bool = True,
    ) -> None:
        self._sender.reply(
            original=original,
            body=body,
            html=html,
            attachments=attachments,
            reply_all=reply_all,
            save_to_sent=save_to_sent,
        )

    def forward(
        self,
        original: Message,
        to: Union[str, list[str]],
        body: str = "",
        *,
        attachments: Optional[list[AttachmentLike]] = None,
        save_to_sent: bool = True,
    ) -> None:
        self._sender.forward(
            original=original,
            to=to,
            body=body,
            attachments=attachments,
            save_to_sent=save_to_sent,
        )

    def __enter__(self) -> Email:
        return self.connect()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __repr__(self) -> str:
        state = "connected" if self.is_connected else "disconnected"
        return f"Email(server={self.server!r}, user={self.user!r}, {state})"
