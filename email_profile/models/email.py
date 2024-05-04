from datetime import datetime
from dataclasses import dataclass, field

from email_profile.abstract import AbstractModel


@dataclass
class EmailModel(AbstractModel):

    class Meta:
        table_name = 'email'

    id: int = field(default=None)
    body_text_plain: str = field(default=None)
    body_text_html: str = field(default=None)
    return_path: str = field(default=None)
    delivered_to: str = field(default=None)
    received: str = field(default=None)
    dkim_signature: str = field(default=None)
    received: str = field(default=None)
    content_type: str = field(default=None)
    date: datetime = field(default=None)
    from_who: str = field(default=None)
    mime_version: str = field(default=None)
    message_id: str = field(default=None)
    subject: str = field(default=None)
    reply_to: str = field(default=None)
    precedence: str = field(default=None)
    x_sg_eid: str = field(default=None)
    x_sg_id: str = field(default=None)
    to_who: str = field(default=None)
    x_entity_id: str = field(default=None)

    def validate_body_text_plain(self, field) -> str:
        if self.body_text_plain:
            return str(self.body_text_plain)
        return ''

    def validate_date(self, field) -> str:
        if self.date:
            return self.date.strftime('%Y-%d-%m %H:%M:%S')
        return ''
