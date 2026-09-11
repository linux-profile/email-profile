"""Argument types shared by the tools, so a constraint lives in one place."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

Uid = Annotated[
    str,
    Field(
        pattern=r"^\d+$",
        description="One message uid from search_messages. Digits only: "
        "ranges and sets are refused so a call touches one message.",
    ),
]

Mailbox = Annotated[
    str,
    Field(
        min_length=1,
        description="Exact server-side name from list_mailboxes.",
    ),
]
