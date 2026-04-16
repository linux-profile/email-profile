"""SQLAlchemy ORM model for raw email storage."""

from __future__ import annotations

from sqlalchemy import Column, String, Text

from email_profile.storage.db import Base


class RawModel(Base):
    """Complete RFC822 source (with attachments in base64)."""

    __tablename__ = "raw"

    message_id = Column(String, primary_key=True)
    uid = Column(String, nullable=False, index=True)
    mailbox = Column(String, nullable=False, index=True)
    flags = Column(String, nullable=False, default="")
    file = Column(Text)
