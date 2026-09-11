"""SMTP tools: send, reply, forward. Registered only with ``allow_send``."""

from __future__ import annotations

from typing import Annotated, Any, Optional, Union

from pydantic import Field

from email_profile.mcp.annotations import SENDS
from email_profile.mcp.config import Settings
from email_profile.mcp.params import Mailbox, Uid
from email_profile.mcp.results import Outcome
from email_profile.mcp.session import Session, guarded

Recipients = Annotated[
    Union[str, list[str]],
    Field(description="One address, a list, or a comma-separated string."),
]


def split(value: Optional[Union[str, list[str]]]) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [v.strip() for v in value if v.strip()]
    return [part.strip() for part in value.split(",") if part.strip()]


def register(mcp: Any, session: Session, settings: Settings) -> None:
    if not settings.allow_send:
        return

    @mcp.tool(annotations=SENDS)
    @guarded
    def send_email(
        to: Recipients,
        subject: str,
        body: str = "",
        html: Optional[str] = None,
        cc: Optional[Recipients] = None,
        bcc: Optional[Recipients] = None,
        reply_to: Optional[str] = None,
    ) -> Outcome:
        """Send a new email from the connected account. Irreversible.

        Show the user the recipients, subject and body before calling —
        there is no draft step and no undo. `body` is plain text; pass
        `html` as well for a rich version.
        """
        with session.lock:
            session.email.send(
                to=split(to),
                subject=subject,
                body=body,
                html=html,
                cc=split(cc) or None,
                bcc=split(bcc) or None,
                reply_to=reply_to,
            )
        return Outcome(action="send", detail=", ".join(split(to)))

    @mcp.tool(annotations=SENDS)
    @guarded
    def reply_message(
        mailbox: Mailbox,
        uid: Uid,
        body: str,
        reply_all: Annotated[
            bool, Field(description="Also reply to every To/Cc address.")
        ] = False,
    ) -> Outcome:
        """Reply to a message, keeping the thread headers. Irreversible.

        Subject, recipients and In-Reply-To come from the original; only
        `body` is yours. Confirm the text with the user first.
        """
        with session.lock:
            original = session.fetch(mailbox, uid)
            session.email.reply(original, body, reply_all=reply_all)
        return Outcome(action="reply", mailbox=mailbox, uid=uid)

    @mcp.tool(annotations=SENDS)
    @guarded
    def forward_message(
        mailbox: Mailbox,
        uid: Uid,
        to: Recipients,
        body: str = "",
    ) -> Outcome:
        """Forward a message, attachments included. Irreversible."""
        with session.lock:
            original = session.fetch(mailbox, uid)
            session.email.forward(original, to=split(to), body=body)
        return Outcome(
            action="forward",
            mailbox=mailbox,
            uid=uid,
            detail=", ".join(split(to)),
        )
