"""SQLAlchemy ORM model for persisted email rows."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Column, DateTime, String, Text

from email_profile.storage.db import Base

if TYPE_CHECKING:
    from email_profile.serializers.email import EmailSerializer


class EmailModel(Base):
    """Persisted email row."""

    __tablename__ = "email"

    id = Column(String, primary_key=True, index=True)
    uid = Column(String, index=True)
    date = Column(DateTime, nullable=True)
    mailbox = Column(String, index=True)

    from_ = Column("from", String, nullable=True)
    to_ = Column("to", String, nullable=True)
    cc = Column(String, nullable=True)
    bcc = Column(String, nullable=True)
    sender = Column(String, nullable=True)
    reply_to = Column(String, nullable=True)

    subject = Column(String, nullable=True)
    file = Column(Text)
    body_text_plain = Column(Text, nullable=True)
    body_text_html = Column(Text, nullable=True)

    content_type = Column(String, nullable=True)
    mime_version = Column(String, nullable=True)
    content_transfer_encoding = Column(String, nullable=True)

    in_reply_to = Column(String, nullable=True)
    references = Column(Text, nullable=True)

    return_path = Column(String, nullable=True)
    delivered_to = Column(String, nullable=True)
    received = Column(Text, nullable=True)

    dkim_signature = Column(Text, nullable=True)
    authentication_results = Column(Text, nullable=True)
    arc_authentication_results = Column(Text, nullable=True)
    arc_message_signature = Column(Text, nullable=True)
    arc_seal = Column(Text, nullable=True)

    list_id = Column(String, nullable=True)
    list_unsubscribe = Column(Text, nullable=True)
    list_unsubscribe_post = Column(String, nullable=True)
    list_post = Column(String, nullable=True)
    list_help = Column(String, nullable=True)
    list_archive = Column(String, nullable=True)
    list_owner = Column(String, nullable=True)

    importance = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    x_priority = Column(String, nullable=True)
    sensitivity = Column(String, nullable=True)
    auto_submitted = Column(String, nullable=True)
    precedence = Column(String, nullable=True)

    x_sg_eid = Column(String, nullable=True)
    x_sg_id = Column(String, nullable=True)
    x_entity_id = Column(String, nullable=True)

    headers = Column(JSON, nullable=True)

    @classmethod
    def from_serializer(cls, serializer: EmailSerializer) -> EmailModel:
        data = serializer.model_dump(by_alias=False, exclude={"attachments"})
        return cls(**data)
