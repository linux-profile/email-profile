from dataclasses import dataclass, field

from email_profile.abstract import AbstractModel


@dataclass
class AttachmentModel(AbstractModel):

    class Meta:
        table_name = 'attachment'

    id: int = field(default=None)
    file_name: str = field(default=None)
    content_type: str = field(default=None)
    content_ascii: str = field(default=None)
