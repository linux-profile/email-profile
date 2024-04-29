from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class EmailModel:

    __tablename__ = 'email'

    id: Optional[int] = field(default=None)
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
