from peewee import (
    TextField,
    IntegerField
)

from email_profile.models.peewee.base import BaseModel


class Attachment(BaseModel):

    id = IntegerField(default=None, null=True)
    file_name = TextField(default=None, null=True)
    content_type = TextField(default=None, null=True)
    content_ascii = TextField(default=None, null=True)
