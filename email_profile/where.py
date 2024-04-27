"""
Where Module
"""

from datetime import date
from typing import Optional, List

from email_profile.dataclass import WhereDataClass
from email_profile.utils import Status, Mode, Mailbox


class Where:

    _data = []
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

        status, data = self.server.search(None, WhereDataClass(**options).result())
        self._status = Status.validate(status)
        self._data = data[0].decode().split(' ')

        return self

    def execute(self) -> List[str]:
        status, messages = self.server.fetch(
            ','.join(self._data), '(RFC822)'
        )
        return self._data
