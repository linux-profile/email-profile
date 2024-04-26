from uuid import uuid4
from sqlalchemy import Column, String, TEXT, ForeignKey
from database import Base, engine

class MailBox(Base):

    __tablename__ = "mailbox"
    __table_args__ = {'extend_existing': True}

    id = Column(String(32), primary_key=True, default=uuid4().hex, index=True)
    name = Column(String)


Base.metadata.create_all(bind=engine)