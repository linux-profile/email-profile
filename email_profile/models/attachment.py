from uuid import uuid4
from sqlalchemy import Column, String, TEXT, ForeignKey
from database import Base, engine

from models.email import Email


class Attachment(Base):

    __tablename__ = "attachment"
    __table_args__ = {'extend_existing': True}

    id = Column(String(32), primary_key=True, default=uuid4().hex, index=True)
    email_id = Column(String(32), ForeignKey(Email.id), index=True)
    file_name = Column(String)
    content_type = Column(String)
    content_ascii = Column(TEXT)


Base.metadata.create_all(bind=engine)