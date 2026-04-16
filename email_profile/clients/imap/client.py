"""IMAP session lifecycle: connect, close, noop."""

from __future__ import annotations

import imaplib
from typing import Optional

from email_profile._internal import _state
from email_profile.clients.imap.mailbox import MailBox
from email_profile.core.errors import ConnectionFailure, NotConnected


class ImapClient:
    """Owns the IMAP socket and the discovered mailbox map."""

    def __init__(
        self,
        *,
        server: str,
        user: str,
        password: str,
        port: int = 993,
        ssl: bool = True,
    ) -> None:
        self.server = server
        self.user = user
        self.password = password
        self.port = port
        self.ssl = ssl
        self.client: Optional[imaplib.IMAP4_SSL] = None
        self.mailboxes: dict[str, MailBox] = {}

    @property
    def is_connected(self) -> bool:
        return self.client is not None

    def connect(self) -> ImapClient:
        try:
            client = imaplib.IMAP4_SSL(self.server)
            client.login(user=self.user, password=self.password)
        except Exception as error:
            raise ConnectionFailure() from error

        self.client = client
        self.mailboxes = {
            mb.name: mb
            for mb in (
                MailBox.from_imap_detail(client=client, detail=detail)
                for detail in _state(client.list())
            )
        }
        return self

    def close(self) -> None:
        if self.client is not None:
            try:
                self.client.logout()
            finally:
                self.client = None
                self.mailboxes = {}
                self.password = None

    def noop(self) -> None:
        self.require()
        self.client.noop()

    def require(self) -> None:
        if self.client is None:
            raise NotConnected()
