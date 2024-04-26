from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Integer
from database import Base, engine


class Email(Base):
    """
    Return-Path
    Delivered-To
    Received
    DKIM-Signature
    Received
    Content-Type
    Date
    From
    Mime-Version
    Message-ID
    Subject
    Reply-To
    Precedence
    X-SG-EID
    X-SG-ID
    To
    X-Entity-ID
    """

    __tablename__ = "email"
    __table_args__ = {'extend_existing': True}

    id = Column(String(32), primary_key=True, default=uuid4().hex, index=True)
    number = Column(Integer)
    body_text_plain = Column(String)
    body_text_html = Column(String)
    return_path = Column(String)
    delivered_to = Column(String)
    received = Column(String)
    dkim_signature = Column(String)
    received = Column(String)
    content_type = Column(String)
    date = Column(DateTime)
    _from = Column('from', String)
    mime_version = Column(String)
    message_id = Column(String, unique=True, primary_key=True)
    subject = Column(String)
    reply_to = Column(String)
    precedence = Column(String)
    x_sg_eid = Column(String)
    x_sg_id = Column(String)
    to = Column(String)
    x_entity_id = Column(String)


Base.metadata.create_all(bind=engine)