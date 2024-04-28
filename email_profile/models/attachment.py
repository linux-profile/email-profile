from uuid import uuid4
from sqlalchemy import Column, String, Integer, TEXT, ForeignKey

from email_profile.config.database import Base, engine
from email_profile.models.email import EmailModel


class AttachmentModel(Base):

    __tablename__ = "attachment"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey(EmailModel.id), index=True)
    file_name = Column(String)
    content_type = Column(String)
    content_ascii = Column(TEXT)


Base.metadata.create_all(bind=engine)