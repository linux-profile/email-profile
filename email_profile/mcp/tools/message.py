"""Message tools: read one, handle attachments, change flags, move."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Optional

from pydantic import Field

from email_profile.mcp.annotations import DESTRUCTIVE, READ_ONLY, REVERSIBLE
from email_profile.mcp.config import Settings
from email_profile.mcp.params import Mailbox, Uid
from email_profile.mcp.results import AttachmentInfo, MessageDetail, Outcome
from email_profile.mcp.session import Session, ToolError, guarded


def _confine(root: str, directory: str) -> Path:
    """``root/directory`` resolved, or a ``ToolError`` when it escapes."""
    base = Path(root).resolve()
    target = (base / directory).resolve()
    if target != base and base not in target.parents:
        raise ToolError(
            f"directory={directory!r} is outside the attachments root; "
            "use a relative path."
        )
    return target


def register(mcp: Any, session: Session, settings: Settings) -> None:
    _register_read(mcp, session, settings)
    _register_flags(mcp, session)
    if settings.allow_delete:
        _register_delete(mcp, session)


def _register_read(mcp: Any, session: Session, settings: Settings) -> None:
    @mcp.tool(annotations=READ_ONLY)
    @guarded
    def read_message(
        mailbox: Mailbox,
        uid: Uid,
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
    @guarded
    def list_attachments(mailbox: Mailbox, uid: Uid) -> list[AttachmentInfo]:
        """List attachments (name, type, size) of one message.

        Content is never returned; use `save_attachment` to write one to
        disk.
        """
        return MessageDetail.of_message(
            session.fetch(mailbox, uid), 0
        ).attachment_list

    @mcp.tool(annotations=REVERSIBLE)
    @guarded
    def save_attachment(
        mailbox: Mailbox,
        uid: Uid,
        file_name: str,
        directory: Annotated[
            str,
            Field(
                description="Subdirectory of the server's attachments "
                "root; created if missing. Paths outside it are refused."
            ),
        ] = ".",
    ) -> Outcome:
        """Write one attachment to disk and return its path.

        Writes only under the operator's attachments root
        (``EMAIL_MCP_ATTACHMENTS_DIR``, default: the working directory).
        """
        target = _confine(settings.attachments_dir, directory)
        msg = session.fetch(mailbox, uid)
        for attachment in msg.attachments:
            if attachment.file_name == file_name:
                path = attachment.save(target)
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
    @guarded
    def mark_seen(mailbox: Mailbox, uid: Uid) -> Outcome:
        """Mark a message as read."""
        with session.lock:
            session.email.mailbox(mailbox).mark_seen(uid)
        return Outcome(action="mark_seen", mailbox=mailbox, uid=uid)

    @mcp.tool(annotations=REVERSIBLE)
    @guarded
    def mark_unseen(mailbox: Mailbox, uid: Uid) -> Outcome:
        """Mark a message as unread."""
        with session.lock:
            session.email.mailbox(mailbox).mark_unseen(uid)
        return Outcome(action="mark_unseen", mailbox=mailbox, uid=uid)

    @mcp.tool(annotations=REVERSIBLE)
    @guarded
    def flag_message(mailbox: Mailbox, uid: Uid) -> Outcome:
        """Flag (star) a message."""
        with session.lock:
            session.email.mailbox(mailbox).flag(uid)
        return Outcome(action="flag", mailbox=mailbox, uid=uid)

    @mcp.tool(annotations=REVERSIBLE)
    @guarded
    def unflag_message(mailbox: Mailbox, uid: Uid) -> Outcome:
        """Remove the flag (star) from a message."""
        with session.lock:
            session.email.mailbox(mailbox).unflag(uid)
        return Outcome(action="unflag", mailbox=mailbox, uid=uid)

    @mcp.tool(annotations=REVERSIBLE)
    @guarded
    def move_message(
        mailbox: Mailbox, uid: Uid, destination: Mailbox
    ) -> Outcome:
        """Move a message to another mailbox.

        `destination` must be an exact name from `list_mailboxes`. The
        message gets a new uid there; search again to find it.
        """
        with session.lock:
            session.email.mailbox(mailbox).move(uid, destination)
        return Outcome(
            action="move", mailbox=mailbox, uid=uid, detail=destination
        )


def _register_delete(mcp: Any, session: Session) -> None:
    @mcp.tool(annotations=DESTRUCTIVE)
    @guarded
    def delete_message(
        mailbox: Mailbox,
        uid: Uid,
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
        with session.lock:
            session.email.mailbox(mailbox).delete(uid, expunge=expunge)
        return Outcome(
            action="delete",
            mailbox=mailbox,
            uid=uid,
            detail="expunged" if expunge else "flagged",
        )
