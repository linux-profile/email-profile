from dataclasses import dataclass, field


@dataclass
class MailBoxModel:

    __tablename__ = "mailbox"

    id: int = field(default=None)
    name: str = field(default=None)
