"""
Where Module
"""


from datetime import date
from typing import Optional, List

from email_profile.status import Status
from email_profile.message import Message
from email_profile.serializers import WhereSerializer


class Mailbox:

    INBOX = "INBOX"
    SENT = "INBOX.Sent"
    JUNK = "INBOX.Junk"
    DRAFTS = "INBOX.Drafts"


class Mode:

    ALL = "ALL"
    UNSEEN = "UNSEEN"


class Where:

    _data = []
    _message = []
    _status = False
    _total = 0

    def __init__(self,
                 mailbox: Mailbox = Mailbox.INBOX,
                 server: any = None) -> None:
        self.mailbox = mailbox
        self.server = server

    def where(self,
              since: Optional[date] = None,
              before: Optional[date] = None,
              subject: Optional[str] = None,
              from_who: Optional[str] = None) -> object:
        variables = locals().copy()
        options = {}

        for item in variables:
            if variables[item] and item != 'self':
                options[item] = variables[item]

        status, total = self.server.select(self.mailbox.capitalize())
        validate = Status.validate_status(status)
        self._status = validate.type
        self._total = int(total[0].decode())

        status, data = self.server.search(
            None, WhereSerializer(**options).result())
        validate = Status.validate_status(status)
        self._status = validate.type
        self._data = Status.validate_data(data)

        return self

    def count(self) -> int:
        return len(self._data)

    def list_id(self) -> List[str]:
        return self._data

    def list_data(self) -> List[any]:
        if self._data:
            _sum = 1
            _sum_searching = 0
            _groups = 1

            while _sum < len(self._data):
                _sum += 100
                _groups += 1

            splited = [self._data[item::_groups] for item in range(_groups)]

            for group_mail in splited:
                _sum_searching += len(group_mail)

                status, messages = self.server.fetch(
                    ','.join(group_mail), '(RFC822)'
                )
                messages = [message for message in messages if message != b')']

                print(f"Loading: {_sum_searching}/{len(self._data)}", end="\r")

                for reference, text in messages:
                    _id = int(reference.split()[0])
                    self._message.append(Message(text, _id).result())

        return self._message
