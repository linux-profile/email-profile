"""Test fixtures: a fake IMAP server good enough for Email/MailBox/Where."""

from __future__ import annotations

from collections.abc import Iterable
from unittest.mock import MagicMock

SAMPLE_RFC822 = (
    b"Message-ID: <abc@example.com>\r\n"
    b"From: Alice <alice@example.com>\r\n"
    b"To: Bob <bob@example.com>\r\n"
    b"Date: Tue, 1 Jan 2030 12:00:00 +0000\r\n"
    b"Subject: Hello\r\n\r\n"
    b"Hi Bob.\r\n"
)


def make_fake_client(
    *,
    mailboxes: Iterable[bytes] = (
        b'(\\HasNoChildren) "/" "INBOX"',
        b'(\\HasNoChildren) "/" "Sent"',
    ),
    uids: list[bytes] | None = None,
    fetch: list[tuple[bytes, bytes]] | None = None,
) -> MagicMock:
    client = MagicMock()
    client.login.return_value = ("OK", [b"Logged in"])
    client.list.return_value = ("OK", list(mailboxes))
    client.select.return_value = ("OK", [b"1"])
    client.uid.side_effect = lambda command, *args: {  # noqa: ARG005
        "search": ("OK", [b" ".join(uids or [b"1", b"2"])]),
        "fetch": (
            "OK",
            fetch or [(b"1 (RFC822 {%d}" % len(SAMPLE_RFC822), SAMPLE_RFC822)],
        ),
    }[command]
    client.append.return_value = ("OK", [b"APPEND completed"])
    client.logout.return_value = ("BYE", [b"Logging out"])
    return client
