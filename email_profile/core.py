"""
Core Module
"""

import imaplib
from functools import partial

from email_profile.where import Where


class Email:

    def __init__(self, server: str, user: str, password: str) -> None:
        self.server = imaplib.IMAP4_SSL(server)
        self.server.login(user=user, password=password)
        self.select = partial(Where, server=self.server)
