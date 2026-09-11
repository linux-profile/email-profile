"""One lazy, reconnecting ``Email`` handle shared by every tool."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from email_profile.clients.imap.query import Q

try:
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError as exc:  # pragma: no cover - import guard
    raise ImportError(
        "The MCP server requires the 'mcp' extra: "
        "pip install email-profile[mcp]"
    ) from exc

if TYPE_CHECKING:
    from email_profile.clients.imap.where import FetchMode
    from email_profile.email import Email
    from email_profile.serializers.email import Message

EmailFactory = Callable[[], "Email"]


class Session:
    """Connects on first use and reconnects when the link drops."""

    def __init__(self, factory: EmailFactory) -> None:
        self._factory = factory
        self._email: Optional[Email] = None

    @property
    def email(self) -> Email:
        if self._email is None:
            self._email = self._factory()
        if not self._email.is_connected:
            self._email.connect()
        return self._email

    def fetch(
        self, mailbox: str, uid: str, mode: FetchMode = "full"
    ) -> Message:
        """One message by uid, or a ``ToolError`` the model can act on."""
        where = self.email.mailbox(mailbox).where(Q.uid(uid))
        for msg in where.messages(mode=mode, chunk_size=1):
            return msg
        raise ToolError(f"No message with uid={uid!r} in {mailbox!r}.")

    def close(self) -> None:
        if self._email is not None and self._email.is_connected:
            self._email.close()
