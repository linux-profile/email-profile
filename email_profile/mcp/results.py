"""What each tool answers with, so a model knows where to look.

Every shape is closed: the server builds the answer itself from a parsed
``Message``, so there is nothing a provider could add behind our back.
Attachments are metadata only — bytes never cross the wire; use
``save_attachment`` to put one on disk.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from email_profile.serializers.email import Message


class AttachmentInfo(BaseModel):
    """One attachment, without its content."""

    file_name: str
    content_type: str
    size: int = Field(description="Size in bytes.")


class MessageSummary(BaseModel):
    """One row of a search: headers only, no body."""

    uid: str = Field(
        description="Server-side id, unique inside its mailbox. Pass it "
        "with `mailbox` to every other tool."
    )
    mailbox: str
    message_id: str | None = None
    date: str | None = Field(default=None, description="ISO 8601.")
    from_: str | None = Field(default=None, alias="from")
    to: str | None = None
    cc: str | None = None
    subject: str | None = None
    attachments: int = Field(description="How many attachments it carries.")

    model_config = {"populate_by_name": True}

    @classmethod
    def of(cls, msg: Message) -> MessageSummary:
        return cls.model_validate(
            {
                "uid": msg.uid,
                "mailbox": msg.mailbox,
                "message_id": msg.message_id,
                "date": msg.date.isoformat() if msg.date else None,
                "from": msg.from_,
                "to": msg.to_,
                "cc": msg.cc,
                "subject": msg.subject,
                "attachments": len(msg.attachments),
            }
        )


class MessageDetail(MessageSummary):
    """One message with its body, truncated to what was asked for."""

    bcc: str | None = None
    reply_to: str | None = None
    in_reply_to: str | None = None
    references: str | None = None
    content_type: str | None = None
    body: str = Field(
        description="Plain text when the message has it, otherwise the "
        "HTML part. Ends with a `[truncated N chars]` marker when cut."
    )
    truncated: bool = False
    attachment_list: list[AttachmentInfo] = Field(default_factory=list)

    @classmethod
    def of_message(cls, msg: Message, max_chars: int) -> MessageDetail:
        text = (msg.body_text_plain or msg.body_text_html).strip()
        body, truncated = truncate(text, max_chars)
        summary = MessageSummary.of(msg)
        return cls(
            **summary.model_dump(by_alias=True),
            bcc=msg.bcc,
            reply_to=msg.reply_to,
            in_reply_to=msg.in_reply_to,
            references=msg.references,
            content_type=msg.content_type,
            body=body,
            truncated=truncated,
            attachment_list=[
                AttachmentInfo(
                    file_name=a.file_name,
                    content_type=a.content_type,
                    size=len(a.content),
                )
                for a in msg.attachments
            ],
        )


class SearchPage(BaseModel):
    """A page of matches, newest first."""

    mailbox: str
    total: int = Field(description="How many match, not how many are here.")
    offset: int
    limit: int
    next_offset: int | None = Field(
        default=None, description="Pass as `offset` for the next page."
    )
    messages: list[MessageSummary] = Field(default_factory=list)


class Outcome(BaseModel):
    """Acknowledgement of a write."""

    ok: bool = True
    action: str
    mailbox: str | None = None
    uid: str | None = None
    detail: str | None = None


def truncate(text: str, max_chars: int) -> tuple[str, bool]:
    if max_chars <= 0 or len(text) <= max_chars:
        return text, False
    cut = len(text) - max_chars
    return text[:max_chars] + f"\n…[truncated {cut} chars]", True
