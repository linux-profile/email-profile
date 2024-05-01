from dataclasses import dataclass, field

from email_profile.models.dataclass.base import BaseModel


@dataclass
class MailBoxModel(BaseModel):

    class Meta:
        table_name = 'mailbox'

    id: int = field(default=None)
    name: str = field(default=None)
