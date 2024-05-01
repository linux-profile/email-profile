from peewee import (
    TextField,
    DateTimeField,
    IntegerField
)
from email_profile.models.peewee.base import BaseModel


class Email(BaseModel):

    id = IntegerField(primary_key=True)
    body_text_plain = TextField(default=None, null=True)
    body_text_html = TextField(default=None, null=True)
    return_path = TextField(default=None, null=True)
    delivered_to = TextField(default=None, null=True)
    received = TextField(default=None, null=True)
    dkim_signature = TextField(default=None, null=True)
    received = TextField(default=None, null=True)
    content_type = TextField(default=None, null=True)
    date = DateTimeField(default=None, null=True)
    from_who = TextField(default=None, null=True)
    mime_version = TextField(default=None, null=True)
    message_id = TextField(default=None, null=True)
    subject = TextField(default=None, null=True)
    reply_to = TextField(default=None, null=True)
    precedence = TextField(default=None, null=True)
    x_sg_eid = TextField(default=None, null=True)
    x_sg_id = TextField(default=None, null=True)
    to_who = TextField(default=None, null=True)
    x_entity_id = TextField(default=None, null=True)
