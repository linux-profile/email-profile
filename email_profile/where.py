"""
Where Module
"""

from datetime import date
from typing import Optional, List

from email_profile.serializers import WhereSerializer
from email_profile.utils import Status, Mode, Mailbox
from email_profile.message import Message


class Where:

    _data = []
    _message = []
    _status = False
    _total = 0

    def __init__(self,
                 mode: Mode = Mode.ALL,
                 mailbox: Mailbox = Mailbox.INBOX,
                 server: any = None
        ) -> None:
        self.mode = mode
        self.mailbox = mailbox
        self.server = server

    def where(self,
              since: Optional[date] = None,
              before: Optional[date] = None,
              subject: Optional[str] = None,
              from_who: Optional[str] = None
        ) -> object:
        local = locals().copy()
        options = {}

        for item in local:
            if local[item]:
                options[item] = local[item]

        status, total = self.server.select(self.mailbox.capitalize())
        self._status = Status.validate(status)
        self._total = int(total[0].decode())

        status, data = self.server.search(None, WhereSerializer(**options).result())
        self._status = Status.validate(status)
        self._data = data[0].decode().split(' ')

        return self

    def count(self) -> int:
        return len(self._data)

    def list_id(self) -> List[str]:
        return self._data

    def list_data(self) -> List[any]:
        status, messages = self.server.fetch(','.join(self._data), '(RFC822)')
        messages = [message for message in messages if message != b')']

        for reference, text in messages:
            _id = int(reference.split()[0])
            self._message.append(Message(text, _id).result())

        return self._message
