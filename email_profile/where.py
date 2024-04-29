"""
Where Module
"""


import logging

from datetime import date
from typing import Optional, List

from email_profile.config.controller import (
    AttachmentController,
    EmailController
)
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
                 server: any = None) -> None:
        self.mode = mode
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

        status, data = self.server.search(None, WhereSerializer(**options).result())
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

                status, messages = self.server.fetch(','.join(group_mail), '(RFC822)')
                messages = [message for message in messages if message != b')']

                print(f"Searching: {_sum_searching}/{len(self._data)}")

                for reference, text in messages:
                    _id = int(reference.split()[0])
                    self._message.append(Message(text, _id).result())

        return self._message

    def dump_sqlite(self):
        logging.warning(" Function 'dump_sqlite' not implemented")

        sql_email = EmailController()
        sql_attachmentl = AttachmentController()

        for message in self._message:
            sql_email.create(data=message.email)

            for attachment in message.attachments:
                sql_attachmentl.create(data=attachment)
