"""Tests for ImapClient.connect honoring port and ssl flag."""

from unittest import TestCase
from unittest.mock import MagicMock, patch

from email_profile.clients.imap.client import ImapClient


class TestImapClientConnect(TestCase):
    def _fake_client(self) -> MagicMock:
        client = MagicMock()
        client.list.return_value = ("OK", [])
        return client

    def test_ssl_true_uses_imap4_ssl_with_port(self):
        fake = self._fake_client()
        with (
            patch("imaplib.IMAP4_SSL", return_value=fake) as ssl_cls,
            patch("imaplib.IMAP4") as plain_cls,
        ):
            ImapClient(
                server="mail.x", user="u", password="p", port=993, ssl=True
            ).connect()
            ssl_cls.assert_called_once_with("mail.x", 993)
            plain_cls.assert_not_called()

    def test_ssl_false_uses_imap4_with_port(self):
        fake = self._fake_client()
        with (
            patch("imaplib.IMAP4_SSL") as ssl_cls,
            patch("imaplib.IMAP4", return_value=fake) as plain_cls,
        ):
            ImapClient(
                server="127.0.0.1",
                user="u",
                password="p",
                port=1143,
                ssl=False,
            ).connect()
            plain_cls.assert_called_once_with("127.0.0.1", 1143)
            ssl_cls.assert_not_called()

    def test_custom_ssl_port_passed_through(self):
        fake = self._fake_client()
        with patch("imaplib.IMAP4_SSL", return_value=fake) as ssl_cls:
            ImapClient(
                server="mail.x", user="u", password="p", port=9993, ssl=True
            ).connect()
            ssl_cls.assert_called_once_with("mail.x", 9993)
