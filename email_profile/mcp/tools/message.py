"""Message tools: read one, handle attachments, change flags, move."""

from __future__ import annotations

from typing import Annotated, Any, Optional

from pydantic import Field

from email_profile.mcp.annotations import DESTRUCTIVE, READ_ONLY, REVERSIBLE
from email_profile.mcp.config import Settings
from email_profile.mcp.results import AttachmentInfo, MessageDetail, Outcome
from email_profile.mcp.session import Session, ToolError


def register(mcp: Any, session: Session, settings: Settings) -> None:
    _register_read(mcp, session, settings)
    _register_flags(mcp, session)
    if settings.allow_delete:
        _register_delete(mcp, session)


def _register_read(mcp: Any, session: Session, settings: Settings) -> None:
    @mcp.tool(annotations=READ_ONLY)
    def read_message(
        mailbox: str,
        uid: str,
        max_chars: Annotated[
            Optional[int],
            Field(
                ge=0,
                description="Body length cap in characters; 0 disables "
                "truncation. Omit for the server default.",
            ),
        ] = None,
    ) -> MessageDetail:
        """Read one message: headers, body and attachment metadata.

        Body is plain text when the message has it, else its HTML part.
        When `truncated` is true, call again with a larger `max_chars`
        rather than guessing what was cut.
        """
        cap = settings.max_chars if max_chars is None else max_chars
        return MessageDetail.of_message(session.fetch(mailbox, uid), cap)

    @mcp.tool(annotations=READ_ONLY)
    def list_attachments(mailbox: str, uid: str) -> list[AttachmentInfo]:
        """List attachments (name, type, size) of one message.

        Content is never returned; use `save_attachment` to write one to
        disk.
        """
        return MessageDetail.of_message(
            session.fetch(mailbox, uid), 0
        ).attachment_list

    @mcp.tool(annotations=REVERSIBLE)
    def save_attachment(
        mailbox: str,
        uid: str,
        file_name: str,
        directory: Annotated[
            str, Field(description="Local directory; created if missing.")
        ] = ".",
    ) -> Outcome:
        """Write one attachment to disk and return its path."""
        msg = session.fetch(mailbox, uid)
        for attachment in msg.attachments:
            if attachment.file_name == file_name:
                path = attachment.save(directory)
                return Outcome(
                    action="save_attachment",
                    mailbox=mailbox,
                    uid=uid,
                    detail=str(path),
                )
        raise ToolError(
            f"No attachment named {file_name!r} on uid={uid!r}; "
            "call list_attachments for the exact names."
        )


def _register_flags(mcp: Any, session: Session) -> None:
    @mcp.tool(annotations=REVERSIBLE)
    def mark_seen(mailbox: str, uid: str) -> Outcome:
        """Mark a message as read."""
        session.email.mailbox(mailbox).mark_seen(uid)
        return Outcome(action="mark_seen", mailbox=mailbox, uid=uid)

    @mcp.tool(annotations=REVERSIBLE)
    def mark_unseen(mailbox: str, uid: str) -> Outcome:
        """Mark a message as unread."""
        session.email.mailbox(mailbox).mark_unseen(uid)
        return Outcome(action="mark_unseen", mailbox=mailbox, uid=uid)

    @mcp.tool(annotations=REVERSIBLE)
    def flag_message(mailbox: str, uid: str) -> Outcome:
        """Flag (star) a message."""
        session.email.mailbox(mailbox).flag(uid)
        return Outcome(action="flag", mailbox=mailbox, uid=uid)

    @mcp.tool(annotations=REVERSIBLE)
    def unflag_message(mailbox: str, uid: str) -> Outcome:
        """Remove the flag (star) from a message."""
        session.email.mailbox(mailbox).unflag(uid)
        return Outcome(action="unflag", mailbox=mailbox, uid=uid)

    @mcp.tool(annotations=REVERSIBLE)
    def move_message(mailbox: str, uid: str, destination: str) -> Outcome:
        """Move a message to another mailbox.

        `destination` must be an exact name from `list_mailboxes`. The
        message gets a new uid there; search again to find it.
        """
        session.email.mailbox(mailbox).move(uid, destination)
        return Outcome(
            action="move", mailbox=mailbox, uid=uid, detail=destination
        )


def _register_delete(mcp: Any, session: Session) -> None:
    @mcp.tool(annotations=DESTRUCTIVE)
    def delete_message(
        mailbox: str,
        uid: str,
        expunge: Annotated[
            bool,
            Field(description="Remove now instead of only flagging."),
        ] = False,
    ) -> Outcome:
        """Flag a message as deleted; with `expunge`, remove it for good.

        Without `expunge` the server keeps it until the mailbox is
        expunged, and `undelete` on the library side can bring it back.
        Confirm with the user before calling with `expunge=true`.
        """
        session.email.mailbox(mailbox).delete(uid, expunge=expunge)
        return Outcome(
            action="delete",
            mailbox=mailbox,
            uid=uid,
            detail="expunged" if expunge else "flagged",
        )
