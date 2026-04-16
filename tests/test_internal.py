"""Tests for Status.state() helper."""

from unittest import TestCase

from email_profile.core.errors import IMAPError
from email_profile.core.status import Status


class TestState(TestCase):
    def test_ok_returns_payload(self):
        result = Status.state(("OK", [b"data"]))
        assert result == [b"data"]

    def test_no_raises(self):
        with self.assertRaises(IMAPError):
            Status.state(("NO", [b"error"]))

    def test_bad_raises(self):
        with self.assertRaises(IMAPError):
            Status.state(("BAD", [b"bad command"]))
