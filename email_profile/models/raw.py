"""SQLAlchemy ORM model for raw email storage."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, UniqueConstraint

from email_profile.storage.db import Base


class RawModel(Base):
    """Complete RFC822 source (with attachments in base64)."""

    __tablename__ = "raw"
    __table_args__ = (
        UniqueConstraint("uid", "mailbox", name="uq_uid_mailbox"),
    )

    uid = Column(String, primary_key=True)
    mailbox = Column(String, primary_key=True)
    message_id = Column(String, nullable=False, index=True)
    flags = Column(String, nullable=False, default="")
    file = Column(Text)
