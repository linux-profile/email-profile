"""
Utils Module
"""

class Status:
    """
    URL: https://datatracker.ietf.org/doc/html/rfc3501#section-6.2.3
    Result:
        OK - login completed, now in authenticated state
        NO - login failure: user name or password rejected
        BAD - command unknown or arguments invalid
    """
    OK = 'OK'
    NO = 'NO'
    BAD = 'NO'

    @staticmethod
    def validate(status: str) -> bool:
        data = {
            Status.OK: (True, "login completed, now in authenticated state"),
            Status.NO: (False, "login failure: user name or password rejected"),
            Status.BAD: (False, "command unknown or arguments invalid")
        }.get(status, (False, ""))

        if not status[0]:
            raise Exception(data[1])

        return data[0]


class Mailbox:

    INBOX = "INBOX"
    SENT = "INBOX.Sent"
    JUNK = "INBOX.Junk"
    DRAFTS = "INBOX.Drafts"


class Mode:

    ALL = "ALL"
    UNSEEN = "UNSEEN"
