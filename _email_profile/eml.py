from uuid import uuid4
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator
from sqlalchemy import Column, String, Text, DateTime, Integer
from _email_profile.session import Base, engine


class EmailSerializer(BaseModel):

    id: Optional[str]
    uid: int
    date: Optional[datetime]
    mailbox: str
    _from: Optional[str]
    _to: Optional[str]
    file: str

    @field_validator('id', mode='before')
    @classmethod
    def id_before(cls, value: int) -> str:
        if not value:
            return uuid4().hex
        return value


class EmailModel(Base):
    __tablename__ = "email"

    id = Column(String, primary_key=True, index=True)
    uid = Column(Integer)
    date = Column(DateTime)
    mailbox = Column(String)
    _from = Column("from", String)
    _to = Column("to", String)
    file = Column(Text)


Base.metadata.create_all(bind=engine)
