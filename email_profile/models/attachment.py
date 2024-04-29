from dataclasses import dataclass, field


@dataclass
class AttachmentModel:

    __tablename__ = "attachment"

    id: int = field(default=None)
    email_id: int = field(default=None)
    file_name: str = field(default=None)
    content_type: str = field(default=None)
    content_ascii: str = field(default=None)
