"""One lazy, reconnecting ``Email`` handle shared by every tool."""

from __future__ import annotations

import functools
import threading
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar

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
F = TypeVar("F", bound=Callable[..., Any])


def guarded(fn: F) -> F:
    """Turn any library failure into a ``ToolError`` the model can read.

    ``MCPServer`` hides the message of an unexpected exception behind
    "Error executing tool"; a ``ToolError`` reaches the client verbatim,
    so a wrong mailbox name comes back with the list of valid ones.
    """

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except ToolError:
            raise
        except Exception as exc:
            raise ToolError(f"{type(exc).__name__}: {exc}") from exc

    return wrapper  # type: ignore[return-value]


class Session:
    """Connects on first use and reconnects when the link drops.

    Tools run on worker threads and ``imaplib`` is not thread-safe, so
    every tool body runs under ``lock``: connect-or-reconnect and the
    IMAP commands that follow are serialized.
    """

    def __init__(self, factory: EmailFactory) -> None:
        self._factory = factory
        self._email: Optional[Email] = None
        self.lock = threading.RLock()

    @property
    def email(self) -> Email:
        with self.lock:
            if self._email is None:
                self._email = self._factory()
            if not self._email.is_connected:
                self._email.connect()
            return self._email

    def fetch(
        self, mailbox: str, uid: str, mode: FetchMode = "full"
    ) -> Message:
        """One message by uid, or a ``ToolError`` the model can act on."""
        with self.lock:
            where = self.email.mailbox(mailbox).where(Q.uid(uid))
            for msg in where.messages(mode=mode, chunk_size=1):
                return msg
        raise ToolError(f"No message with uid={uid!r} in {mailbox!r}.")

    def close(self) -> None:
        with self.lock:
            if self._email is not None and self._email.is_connected:
                self._email.close()
