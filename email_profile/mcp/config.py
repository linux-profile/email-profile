"""Runtime settings for the MCP server, read from the environment.

Credentials never travel through tool arguments: the model reads and
sends mail as whoever started the server, and nothing else.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_MAX_CHARS = 4000
DEFAULT_LIMIT = 20
MAX_LIMIT = 200


def _flag(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """What the server is allowed to do and how much it returns.

    ``allow_send`` exposes the SMTP tools; ``allow_delete`` exposes
    ``delete_message``. Both default to off so a misconfigured client
    can only read. ``attachments_dir`` is the only place
    ``save_attachment`` may write.
    """

    allow_send: bool = False
    allow_delete: bool = False
    max_chars: int = DEFAULT_MAX_CHARS
    limit: int = DEFAULT_LIMIT
    default_mailbox: str = "INBOX"
    attachments_dir: str = "."

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            allow_send=_flag(os.getenv("EMAIL_MCP_ALLOW_SEND")),
            allow_delete=_flag(os.getenv("EMAIL_MCP_ALLOW_DELETE")),
            max_chars=int(os.getenv("EMAIL_MCP_MAX_CHARS", DEFAULT_MAX_CHARS)),
            limit=int(os.getenv("EMAIL_MCP_LIMIT", DEFAULT_LIMIT)),
            default_mailbox=os.getenv("EMAIL_MCP_DEFAULT_MAILBOX", "INBOX"),
            attachments_dir=os.getenv("EMAIL_MCP_ATTACHMENTS_DIR", "."),
        )
