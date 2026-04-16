"""Pydantic DTO for email messages."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
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
    sender: Optional[str] = None
    reply_to: Optional[str] = None

    subject: Optional[str] = None
    file: str
    body_text_plain: str = ""
    body_text_html: str = ""

    content_type: Optional[str] = None
    mime_version: Optional[str] = None
    content_transfer_encoding: Optional[str] = None

    in_reply_to: Optional[str] = None
    references: Optional[str] = None

    attachments: list[Attachment] = []

    return_path: Optional[str] = None
    delivered_to: Optional[str] = None
    received: Optional[str] = None

    dkim_signature: Optional[str] = None
    authentication_results: Optional[str] = None
    arc_authentication_results: Optional[str] = None
    arc_message_signature: Optional[str] = None
    arc_seal: Optional[str] = None

    list_id: Optional[str] = None
    list_unsubscribe: Optional[str] = None
    list_unsubscribe_post: Optional[str] = None
    list_post: Optional[str] = None
    list_help: Optional[str] = None
    list_archive: Optional[str] = None
    list_owner: Optional[str] = None

    importance: Optional[str] = None
    priority: Optional[str] = None
    x_priority: Optional[str] = None
    sensitivity: Optional[str] = None
    auto_submitted: Optional[str] = None
    precedence: Optional[str] = None

    x_sg_eid: Optional[str] = None
    x_sg_id: Optional[str] = None
    x_entity_id: Optional[str] = None

    headers: dict[str, Union[str, list[str]]] = {}

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

        return cls(
            id=message_id,
            uid=uid,
            mailbox=mailbox,
            date=date,
            **{"from": from_, "to": to_},
            cc=parsed.cc,
            bcc=parsed.bcc,
            sender=parsed.sender,
            reply_to=parsed.reply_to,
            subject=parsed.subject,
            file=file or raw.decode("utf-8", errors="replace"),
            body_text_plain=parsed.body_text_plain,
            body_text_html=parsed.body_text_html,
            content_type=parsed.content_type,
            mime_version=parsed.mime_version,
            content_transfer_encoding=parsed.content_transfer_encoding,
            in_reply_to=parsed.in_reply_to,
            references=parsed.references,
            attachments=parsed.attachments,
            return_path=parsed.return_path,
            delivered_to=parsed.delivered_to,
            received=parsed.received,
            dkim_signature=parsed.dkim_signature,
            authentication_results=parsed.authentication_results,
            arc_authentication_results=parsed.arc_authentication_results,
            arc_message_signature=parsed.arc_message_signature,
            arc_seal=parsed.arc_seal,
            list_id=parsed.list_id,
            list_unsubscribe=parsed.list_unsubscribe,
            list_unsubscribe_post=parsed.list_unsubscribe_post,
            list_post=parsed.list_post,
            list_help=parsed.list_help,
            list_archive=parsed.list_archive,
            list_owner=parsed.list_owner,
            importance=parsed.importance,
            priority=parsed.priority,
            x_priority=parsed.x_priority,
            sensitivity=parsed.sensitivity,
            auto_submitted=parsed.auto_submitted,
            precedence=parsed.precedence,
            x_sg_eid=parsed.x_sg_eid,
            x_sg_id=parsed.x_sg_id,
            x_entity_id=parsed.x_entity_id,
            headers=parsed.headers,
        )

    def __repr__(self) -> str:
        date = self.date.isoformat() if self.date else "?"
        subj = (self.subject or "")[:40]
        return (
            f"EmailSerializer(uid={self.uid!r}, from={self.from_!r}, "
            f"date={date}, subject={subj!r})"
        )

    def save_json(self, path: Union[str, Path] = "json") -> Path:
        """Write to <path>/<id>.json."""
        from email_profile.storage.dump import MessageDumper

        return MessageDumper(self).to_json(path)

    def save_html(self, path: Union[str, Path] = "html") -> Path:
        """Write the HTML body to <path>/<id>/index.html."""
        from email_profile.storage.dump import MessageDumper

        return MessageDumper(self).to_html(path)

    def save_attachments(
        self, path: Union[str, Path] = "attachments"
    ) -> list[Path]:
        """Save every attachment under <path>/<id>/."""

        target = Path(path) / str(self.id)
        target.mkdir(parents=True, exist_ok=True)

        return [a.save(target) for a in self.attachments]
