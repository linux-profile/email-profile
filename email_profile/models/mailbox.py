from dataclasses import dataclass, field

from email_profile.abstract import AbstractModel


@dataclass
class MailBoxModel(AbstractModel):

    class Meta:
        table_name = 'mailbox'

    id: int = field(default=None)
    name: str = field(default=None)
