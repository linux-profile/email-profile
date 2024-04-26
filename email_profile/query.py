from typing import Dict
from functools import partial


class Mailbox:

    INBOX = "INBOX"
    SENT = "INBOX.Sent"
    JUNK = "INBOX.Junk"
    DRAFTS = "INBOX.Drafts"


class Mode:

    ALL = "ALL"
    UNSEEN = "UNSEEN"


class Select:

    _parts = []
    _context = object

    def __init__(self,
                 mode: Mode = Mode.ALL,
                 mailbox: Mailbox = Mailbox.INBOX,
                 exception: bool = True
        ) -> None:
        self.mode = mode
        self.mailbox = mailbox
        self.exception = exception

        self._context = self
    
    def _check_parts(self):
        checker = []
        for part in self._parts:
            checker.append(part.func.__name__)
            if len(
                list(filter(lambda x: part.func.__name__ in x, checker))
            ) > 1:
                if self.exception:
                    raise Exception(
                        "It is not allowed to include the same functions!"
                    )

    def where(self, query: str) -> object:
        def _where(query):
            return query

        exe = partial(_where, query)
        self._parts.append(exe)
        self._check_parts()

        return self._context

    def count(self) -> object:
        def _count():
            return True

        exe = partial(_count)
        self._parts.append(exe)
        self._check_parts()

        return self._context

    def execute(self) -> Dict:
        query = dict()
        for part in self._parts:
            query[part.func.__name__] = part()

        return query


query = Select(
    mode=Mode.ALL,
    mailbox=Mailbox.INBOX,
    exception=False
).count().where(query="xpto")
query.execute()
