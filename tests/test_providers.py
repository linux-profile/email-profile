from unittest import TestCase
from unittest.mock import patch

from email_profile.core.types import IMAPHost
from email_profile.providers import KNOWN_PROVIDERS, resolve_imap_host


class TestResolveImapHost(TestCase):
    def test_known_provider(self):
        self.assertEqual(
            resolve_imap_host("a@gmail.com"),
            KNOWN_PROVIDERS["gmail.com"],
        )

    def test_unknown_falls_back_to_imap_dot_domain(self):
        with (
            patch("email_profile.providers._lookup_srv", return_value=None),
            patch("email_profile.providers._lookup_mx", return_value=None),
        ):
            host = resolve_imap_host("a@my.test")
        self.assertEqual(host, IMAPHost("imap.my.test"))

    def test_srv_overrides_fallback(self):
        fake = IMAPHost("imap.real.example", port=993)
        with (
            patch("email_profile.providers._lookup_srv", return_value=fake),
            patch("email_profile.providers._lookup_mx", return_value=None),
        ):
            self.assertEqual(resolve_imap_host("a@anything.test"), fake)

    def test_mx_hint_detects_hostinger(self):
        with (
            patch("email_profile.providers._lookup_srv", return_value=None),
            patch(
                "email_profile.providers._lookup_mx",
                return_value=IMAPHost("imap.hostinger.com"),
            ),
        ):
            host = resolve_imap_host("a@x.test")
        self.assertEqual(host.host, "imap.hostinger.com")

    def test_invalid_email_raises(self):
        with self.assertRaises(ValueError):
            resolve_imap_host("no-at-sign")
