from dataclasses import dataclass, field

from email_profile.models.dataclass.base import BaseModel


@dataclass
class AttachmentModel(BaseModel):

    class Meta:
        table_name = 'attachment'

    id: int = field(default=None)
    file_name: str = field(default=None)
    content_type: str = field(default=None)
    content_ascii: str = field(default=None)
