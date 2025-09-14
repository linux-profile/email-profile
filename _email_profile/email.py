"""
Core Module
"""

import re
import imaplib

from uuid import uuid4
from datetime import date, datetime

from email import message_from_bytes
from email.utils import parsedate_to_datetime
from email.utils import parseaddr

from typing import List, Tuple
from functools import partial

from email_profile.status import Status
from _email_profile.eml import EmailModel, EmailSerializer
from _email_profile.session import SessionLocal
from email_profile.serializers import Query


class ConnectionFailure(Exception):

    def __init__(self):
        super(ConnectionFailure, self).__init__(
            "Failed to connect to email server."
        )


def _state(context):
    Status.validate_status(context[0])
    return context[1]


class Storage:

    def __init__(self):
        self.temp = []
        self.db = SessionLocal

    def add(self, messages: List[Tuple[bytes]], mailbox: str):
        for message in messages:
            if isinstance(message, tuple):
                content = message_from_bytes(message[1])

                for decode in ["utf-8", "latin-1"]:
                    try:
                        file = message[1].decode(decode)
                        continue
                    except UnicodeDecodeError as error:
                        import logging
                        logging.error(error)
                try:
                    with self.db() as session:
                        session.begin()

                        breakpoint()

                        # email = EmailSerializer(
                        #     id=content.get("Message-ID"),
                        #     uid=message[0].decode().split()[0],
                        #     date=content.get("Date"),
                        #     _from=content.get("From"),
                        #     _to=content.get("To")
                        # )

                        # breakpoint()

                        _id = content.get("Message-ID") or uuid4().hex
                        _uid = message[0].decode().split()[0]
                        _date = parsedate_to_datetime(content.get("Date")) if content.get("Date") else datetime(1000,1,1)
                        _from = parseaddr(content.get("From"))[1]
                        _to = parseaddr(content.get("To"))[1]

                        db_item = EmailModel(
                            id=_id,
                            uid=_uid,
                            date=_date,
                            mailbox=mailbox,
                            _from=_from,
                            _to=_to,
                            file=file
                        )
                        session.add(db_item)
                        session.commit()
                except Exception as error:
                    import logging
                    logging.error(error)

        self.temp += content


class Email:

    def __init__(self, server: str, user: str, password: str):
        client = imaplib.IMAP4_SSL(server)
        client.login(user=user, password=password)
        self.storage = Storage()
        self.select = Select(client=client, storage=self.storage)

    def load(self, params: Query = {}):
        for mailbox in self.select.mailbox:
            select = getattr(self.select, mailbox)
            select.where(params=params)


class Select:

    def __init__(self, client: imaplib.IMAP4_SSL, storage: Storage):
        self.mailbox: List[str] = []
        result = _state(client.list())

        for detail in result:
            new_mailbox = MailBox(
                client=client,
                detail=detail,
                storage=storage
            )

            self.mailbox.append(new_mailbox.func)
            setattr(self, new_mailbox.func, new_mailbox)


class MailBoxInstance:

    def __init__(self, *_args, **_kwargs):
        self.server = None
        self.delimiter = None
        self.name = None
        self.func = None
        self.where = None


class MailBox(MailBoxInstance):

    PATTERN = re.compile(
        r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)'
    )

    def parse(self, detail: bytes):
        match = self.PATTERN.match(detail.decode("utf-8"))
        return match.groups()

    def __init__(
        self,
        client: imaplib.IMAP4_SSL,
        detail: bytes,
        storage: Storage
    ):
        flags, delimiter, name = self.parse(detail=detail)
        self.func = re.sub(r'[^a-zA-Z]+', '_', name.lower())
        self.flags = [flag.strip("\\") for flag in flags.split()]
        self.delimiter = delimiter
        self.name = name

        self.where = partial(
            Where,
            client=client,
            mailbox=self,
            storage=storage
        )


class Where:

    CHUNK_SIZE = 100

    def __new__(
        cls,
        client: imaplib.IMAP4_SSL,
        mailbox: MailBox,
        storage: Storage,
        params: Query = {},
    ):
        cls.emails = []
        _state(client.select(mailbox.name))

        query = Query(**params)

        data = _state(client.uid("search", None, query.mount()))
        uids = data[0].decode().split()

        groups = [
            uids[uid:uid + cls.CHUNK_SIZE]
            for uid in range(0, len(uids), cls.CHUNK_SIZE)
        ]

        for group in groups:
            if group:
                messages = _state(
                    context=client.uid("fetch", ",".join(group), "(RFC822)")
                )
                storage.add(messages=messages, mailbox=mailbox.name)

        return storage.temp
