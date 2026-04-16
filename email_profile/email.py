"""IMAP client (high-level entry point)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from email_profile.backup import RestoreOps
from email_profile.factories import Credentials, EmailFactories
from email_profile.folders import FolderAccess
from email_profile.imap_session import IMAPSession
from email_profile.providers import resolve_imap_host
from email_profile.queries import QueryShortcuts
from email_profile.searches import Where
from email_profile.sender import Sender
from email_profile.smtp import AttachmentLike

if TYPE_CHECKING:
    from email.message import EmailMessage

    from email_profile.eml import EmailSerializer
    from email_profile.mailbox import MailBox
    from email_profile.protocols import StorageProtocol
    from email_profile.types import SMTPHost


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
    ) -> None:
        creds = self._resolve(server, user, password, port, ssl)

        self._session = IMAPSession(
            server=creds.server,
            user=creds.user,
            password=creds.password,
            port=creds.port,
            ssl=creds.ssl,
        )
        self._folders = FolderAccess(self._session)
        self._queries = QueryShortcuts(self._folders)
        self._backup = RestoreOps(self._session)
        self._sender = Sender(self._session, self._folders)

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
        host = resolve_imap_host(address)
        return cls(
            server=host.host,
            user=address,
            password=password,
            port=host.port,
            ssl=host.ssl,
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

    @classmethod
    def gmail(cls, user: str, password: str) -> Email:
        return cls("imap.gmail.com", user, password)

    @classmethod
    def outlook(cls, user: str, password: str) -> Email:
        return cls("outlook.office365.com", user, password)

    @classmethod
    def icloud(cls, user: str, password: str) -> Email:
        return cls("imap.mail.me.com", user, password)

    @classmethod
    def yahoo(cls, user: str, password: str) -> Email:
        return cls("imap.mail.yahoo.com", user, password)

    @classmethod
    def hostinger(cls, user: str, password: str) -> Email:
        return cls("imap.hostinger.com", user, password)

    @classmethod
    def zoho(cls, user: str, password: str) -> Email:
        return cls("imap.zoho.com", user, password)

    @classmethod
    def fastmail(cls, user: str, password: str) -> Email:
        return cls("imap.fastmail.com", user, password)

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

    def restore(
        self,
        storage: StorageProtocol,
        mailbox: Optional[str] = None,
        target: Optional[str] = None,
        skip_duplicates: bool = True,
    ) -> int:
        return self._backup.restore(
            storage=storage,
            mailbox=mailbox,
            target=target,
            skip_duplicates=skip_duplicates,
        )

    def restore_eml(
        self,
        path: Union[str, Path],
        target: Optional[str] = None,
    ) -> int:
        return self._backup.restore_eml(path=path, target=target)

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
        original: EmailSerializer,
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
        original: EmailSerializer,
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
