"""Pydantic DTO for email messages."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from typing import Optional, Union
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from email_profile.parser import Attachment, ParsedBody, parse_rfc822


class EmailSerializer(BaseModel):
    """One email message as a validated DTO."""

    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True
    )

    id: Optional[str] = None
    uid: str
    date: Optional[datetime] = None
    mailbox: str

    from_: Optional[str] = Field(default=None, alias="from")
    to_: Optional[str] = Field(default=None, alias="to")
    cc: Optional[str] = None
    bcc: Optional[str] = None
    reply_to: Optional[str] = None

    subject: Optional[str] = None
    file: str
    body_text_plain: str = ""
    body_text_html: str = ""
    content_type: Optional[str] = None

    in_reply_to: Optional[str] = None
    references: Optional[str] = None

    list_id: Optional[str] = None
    list_unsubscribe: Optional[str] = None

    headers: dict[str, Union[str, list[str]]] = {}

    attachments: list[Attachment] = []

    @field_validator("id", mode="before")
    @classmethod
    def _default_id(cls, value: Optional[str]) -> str:
        if not value:
            return uuid4().hex
        return value

    @classmethod
    def from_raw(
        cls,
        *,
        uid: str,
        mailbox: str,
        raw: bytes,
        message_id: Optional[str] = None,
        date: Optional[datetime] = None,
        from_: Optional[str] = None,
        to_: Optional[str] = None,
        file: Optional[str] = None,
    ) -> EmailSerializer:
        """Parse RFC822 bytes into a serializer."""

        parsed: ParsedBody = parse_rfc822(raw)

        fallback_id = message_id or sha256(raw).hexdigest()

        return cls(
            id=fallback_id,
            uid=uid,
            mailbox=mailbox,
            date=date,
            **{"from": from_, "to": to_},
            cc=parsed.cc,
            bcc=parsed.bcc,
            reply_to=parsed.reply_to,
            subject=parsed.subject,
            file=file or raw.decode("utf-8", errors="replace"),
            body_text_plain=parsed.body_text_plain,
            body_text_html=parsed.body_text_html,
            content_type=parsed.content_type,
            in_reply_to=parsed.in_reply_to,
            references=parsed.references,
            list_id=parsed.list_id,
            list_unsubscribe=parsed.list_unsubscribe,
            attachments=parsed.attachments,
            headers=parsed.headers,
        )

    def __repr__(self) -> str:
        date = self.date.isoformat() if self.date else "?"
        subj = (self.subject or "")[:40]
        return (
            f"EmailSerializer(uid={self.uid!r}, from={self.from_!r}, "
            f"date={date}, subject={subj!r})"
        )
