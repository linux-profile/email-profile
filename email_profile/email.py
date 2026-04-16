"""IMAP client (high-level entry point)."""

from __future__ import annotations

import imaplib
import os
from datetime import date, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from email_profile._internal import _state
from email_profile.errors import ConnectionFailure, NotConnected
from email_profile.folders import (
    ARCHIVE_HINTS,
    DRAFTS_HINTS,
    INBOX_HINTS,
    SENT_HINTS,
    SPAM_HINTS,
    TRASH_HINTS,
    find_mailbox,
)
from email_profile.mailbox import MailBox
from email_profile.providers import IMAPHost, resolve_imap_host
from email_profile.searches import Where

if TYPE_CHECKING:
    from email_profile.protocols import StorageProtocol


class Email:
    """IMAP client; lazy connect via ``with Email(...) as app:``.

    Constructor overloads::

        Email(user="u@gmail.com", password="pw")          # auto-discover
        Email("u@gmail.com", "pw")                          # same, positional
        Email("imap.gmail.com", "u", "pw")                  # explicit host
        Email(server="...", user="...", password="...")     # full kwargs
        Email()                                              # zero args -> env

    The ``Email.gmail/.../from_env`` classmethods keep working.
    """

    def __init__(
        self,
        server: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 993,
        ssl: bool = True,
    ) -> None:
        if server is None and user is None and password is None:
            built = Email._build_from_env()
            self._server, self._user, self._password = built
            self._port, self._ssl = 993, True
            self._client = None
            self._mailboxes = {}
            return

        if password is None and user is not None and server and "@" in server:
            address, password = server, user
            host: IMAPHost = resolve_imap_host(address)
            server, user = host.host, address
            port, ssl = host.port, host.ssl

        if server is None and user is not None and "@" in user and password:
            host = resolve_imap_host(user)
            server, port, ssl = host.host, host.port, host.ssl

        if server is None or user is None or password is None:
            raise TypeError(
                "Email() requires (server, user, password), "
                "or (user='you@domain', password=...) for auto-discovery, "
                "or no args (env vars)."
            )

        self._server = server
        self._user = user
        self._password = password
        self._port = port
        self._ssl = ssl
        self._client: Optional[imaplib.IMAP4_SSL] = None
        self._mailboxes: dict[str, MailBox] = {}

    @property
    def server(self) -> str:
        """The IMAP server hostname."""
        return self._server

    @property
    def user(self) -> str:
        """The authenticated user / email address."""
        return self._user

    @property
    def port(self) -> int:
        """The IMAP port in use."""
        return self._port

    @property
    def ssl(self) -> bool:
        """Whether the connection uses SSL."""
        return self._ssl

    @property
    def is_connected(self) -> bool:
        """``True`` while an IMAP session is open."""
        return self._client is not None

    @staticmethod
    def _build_from_env(
        server_var: str = "EMAIL_SERVER",
        user_var: str = "EMAIL_USERNAME",
        password_var: str = "EMAIL_PASSWORD",
        load_dotenv: bool = True,
    ) -> tuple[str, str, str]:
        if load_dotenv:
            try:
                from dotenv import load_dotenv as _ld

                _ld()
            except ImportError:
                pass

        user = os.environ.get(user_var)
        password = os.environ.get(password_var)

        if not user or not password:
            raise KeyError(
                f"Missing {user_var!r} or {password_var!r} in environment."
            )

        server = os.environ.get(server_var)
        if not server:
            host = resolve_imap_host(user)
            server = host.host
        return server, user, password

    @classmethod
    def from_email(cls, address: str, password: str) -> Email:
        """Auto-discover the IMAP host from the address."""

        host: IMAPHost = resolve_imap_host(address)

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
        server, user, password = cls._build_from_env(
            server_var=server_var,
            user_var=user_var,
            password_var=password_var,
            load_dotenv=load_dotenv,
        )
        return cls(server=server, user=user, password=password)

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
        """Open the IMAP connection and discover mailboxes."""
        try:
            client = imaplib.IMAP4_SSL(self._server)
            client.login(user=self._user, password=self._password)
        except Exception as error:
            raise ConnectionFailure() from error

        self._client = client

        self._mailboxes = {
            mb.name: mb
            for mb in (
                MailBox.from_imap_detail(client=client, detail=detail)
                for detail in _state(client.list())
            )
        }

        return self

    def close(self) -> None:
        """Close the IMAP connection; safe to call twice."""
        if self._client is not None:
            try:
                self._client.logout()
            finally:
                self._client = None
                self._mailboxes = {}

    def noop(self) -> None:
        """Send IMAP NOOP to keep the connection alive on long jobs."""
        self._require_connection()
        self._client.noop()

    def mailboxes(self) -> list[str]:
        """All mailbox names visible on the server."""
        self._require_connection()
        return list(self._mailboxes)

    def mailbox(self, name: str) -> MailBox:
        """One mailbox by its server-side name."""
        self._require_connection()

        if name not in self._mailboxes:
            raise KeyError(
                f"Unknown mailbox: {name!r}. Available: {self.mailboxes()}"
            )

        return self._mailboxes[name]

    def _find(self, hints: tuple[str, ...]) -> MailBox:
        self._require_connection()
        mb = find_mailbox(self._mailboxes, hints)

        if mb is None:
            raise KeyError(
                f"Could not find a mailbox matching {hints!r}. "
                f"Available: {self.mailboxes()}"
            )

        return mb

    @property
    def inbox(self) -> MailBox:
        return self._find(INBOX_HINTS)

    @property
    def sent(self) -> MailBox:
        return self._find(SENT_HINTS)

    @property
    def spam(self) -> MailBox:
        return self._find(SPAM_HINTS)

    @property
    def trash(self) -> MailBox:
        return self._find(TRASH_HINTS)

    @property
    def drafts(self) -> MailBox:
        return self._find(DRAFTS_HINTS)

    @property
    def archive(self) -> MailBox:
        return self._find(ARCHIVE_HINTS)

    def unread(self) -> Where:
        """Unread messages in the inbox."""
        return self.inbox.where(unseen=True)

    def recent(self, days: int = 7) -> Where:
        """Messages from the last N days."""
        return self.inbox.where(since=date.today() - timedelta(days=days))

    def search(self, text: str) -> Where:
        """Full-text search in the inbox."""
        return self.inbox.where(text=text)

    def all(self) -> Where:
        """All messages in the inbox."""
        return self.inbox.where()

    def restore(
        self,
        storage: StorageProtocol,
        mailbox: Optional[str] = None,
        target: Optional[str] = None,
        skip_duplicates: bool = True,
    ) -> int:
        """Re-upload every message persisted in storage to this server.

        With ``skip_duplicates=True`` (default) any message whose
        ``Message-ID`` already exists in the destination mailbox is
        skipped — making ``restore`` safe to re-run after an interruption.
        """

        self._require_connection()
        count = 0
        seen_ids: dict[str, set[str]] = {}

        for serializer in storage.messages(mailbox=mailbox):
            box_name = target or serializer.mailbox
            if box_name not in self._mailboxes:
                raise KeyError(
                    f"Target mailbox {box_name!r} does not exist. "
                    f"Available: {self.mailboxes()}"
                )

            if skip_duplicates:
                if box_name not in seen_ids:
                    seen_ids[box_name] = self._existing_ids(box_name)
                if serializer.id and serializer.id in seen_ids[box_name]:
                    continue
                if serializer.id:
                    seen_ids[box_name].add(serializer.id)

            self._mailboxes[box_name].append(serializer)
            count += 1

        return count

    def restore_eml(
        self,
        path: Union[str, Path],
        target: Optional[str] = None,
    ) -> int:
        """Re-upload every .eml under path; mailbox = parent dir name."""

        self._require_connection()
        source = Path(path)
        if not source.exists():
            raise FileNotFoundError(source)

        count = 0

        for eml_path in source.rglob("*.eml"):
            box_name = target or eml_path.parent.name
            if box_name not in self._mailboxes:
                raise KeyError(
                    f"Target mailbox {box_name!r} does not exist. "
                    f"Available: {self.mailboxes()}"
                )
            self._mailboxes[box_name].append(eml_path.read_bytes())
            count += 1

        return count

    def _existing_ids(self, mailbox_name: str) -> set[str]:
        """Collect Message-IDs already present in a server mailbox."""
        from email_profile._internal import _state

        ids: set[str] = set()
        client = self._client
        if client is None:
            return ids

        _state(client.select(mailbox_name))
        status, data = client.uid("search", None, "ALL")
        if status != "OK" or not data or not data[0]:
            return ids

        uids = data[0].decode().split()
        if not uids:
            return ids

        # Pull only the Message-ID header — cheap.
        status, fetched = client.uid(
            "fetch", ",".join(uids), "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])"
        )
        if status != "OK":
            return ids

        for entry in fetched:
            if not isinstance(entry, tuple):
                continue
            _, raw = entry
            text = raw.decode("utf-8", errors="replace")
            for line in text.splitlines():
                if line.lower().startswith("message-id:"):
                    ids.add(line.split(":", 1)[1].strip())
                    break
        return ids

    def _require_connection(self) -> None:
        if self._client is None:
            raise NotConnected()

    def __enter__(self) -> Email:
        return self.connect()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __repr__(self) -> str:
        state = "connected" if self.is_connected else "disconnected"
        return f"Email(server={self.server!r}, user={self.user!r}, {state})"
