"""Tests for SMTP host resolution."""

from unittest import TestCase
from unittest.mock import patch

from email_profile.providers import resolve_smtp_host


class TestResolveSmtpHost(TestCase):
    def test_gmail(self):
        host = resolve_smtp_host("user@gmail.com")
        assert host.host == "smtp.gmail.com"

    def test_outlook(self):
        host = resolve_smtp_host("user@outlook.com")
        assert host.host == "smtp.office365.com"
        assert host.port == 587

    def test_yahoo(self):
        host = resolve_smtp_host("user@yahoo.com")
        assert host.host == "smtp.mail.yahoo.com"

    def test_icloud(self):
        host = resolve_smtp_host("user@icloud.com")
        assert host.host == "smtp.mail.me.com"

    def test_unknown_falls_back_to_smtp_dot_domain(self):
        with patch("email_profile.providers._HAS_DNS", False):
            host = resolve_smtp_host("user@custom.org")
            assert host.host == "smtp.custom.org"

    def test_invalid_email_raises(self):
        with self.assertRaises(ValueError):
            resolve_smtp_host("not-an-email")
