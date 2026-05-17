"""Tests for SMTP host resolution covering known + DNS + fallback paths."""

from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from email_profile.providers import (
    SMTP_MX_HINTS,
    ProviderResolutionError,
    _lookup_smtp_mx,
    _lookup_smtp_srv,
    resolve_smtp_host,
)


class _Target:
    def __init__(self, value: str) -> None:
        self._value = value

    def __str__(self) -> str:
        return self._value


def _srv(target: str, port: int, priority: int = 10, weight: int = 5):
    return SimpleNamespace(
        target=_Target(target),
        port=port,
        priority=priority,
        weight=weight,
    )


def _mx(exchange: str, preference: int = 10):
    return SimpleNamespace(exchange=_Target(exchange), preference=preference)


class TestKnownProviders(TestCase):
    def test_gmail(self):
        host = resolve_smtp_host("user@gmail.com")
        self.assertEqual(host.host, "smtp.gmail.com")

    def test_googlemail_alias(self):
        host = resolve_smtp_host("user@googlemail.com")
        self.assertEqual(host.host, "smtp.gmail.com")

    def test_outlook_uses_starttls_587(self):
        host = resolve_smtp_host("user@outlook.com")
        self.assertEqual(host.host, "smtp.office365.com")
        self.assertEqual(host.port, 587)
        self.assertFalse(host.ssl)
        self.assertTrue(host.starttls)

    def test_office365_family(self):
        for d in ("hotmail.com", "live.com", "msn.com", "office365.com"):
            self.assertEqual(
                resolve_smtp_host(f"u@{d}").host, "smtp.office365.com"
            )

    def test_icloud_aliases(self):
        for d in ("icloud.com", "me.com", "mac.com"):
            self.assertEqual(
                resolve_smtp_host(f"u@{d}").host, "smtp.mail.me.com"
            )

    def test_yahoo_and_ymail(self):
        for d in ("yahoo.com", "ymail.com"):
            self.assertEqual(
                resolve_smtp_host(f"u@{d}").host, "smtp.mail.yahoo.com"
            )

    def test_zoho(self):
        self.assertEqual(resolve_smtp_host("u@zoho.com").host, "smtp.zoho.com")

    def test_hostinger(self):
        self.assertEqual(
            resolve_smtp_host("u@hostinger.com").host, "smtp.hostinger.com"
        )

    def test_fastmail(self):
        self.assertEqual(
            resolve_smtp_host("u@fastmail.com").host, "smtp.fastmail.com"
        )

    def test_aol(self):
        self.assertEqual(resolve_smtp_host("u@aol.com").host, "smtp.aol.com")


class TestEmailSplitting(TestCase):
    def test_invalid_email_no_at(self):
        with self.assertRaises(ValueError):
            resolve_smtp_host("not-an-email")

    def test_invalid_email_no_domain(self):
        with self.assertRaises(ValueError):
            resolve_smtp_host("user@")

    def test_invalid_email_no_local_part(self):
        with self.assertRaises(ValueError):
            resolve_smtp_host("@example.com")


class TestUnknownFallback(TestCase):
    def test_falls_back_to_convention_when_no_dns(self):
        with patch("email_profile.providers._HAS_DNS", False):
            host = resolve_smtp_host("user@custom.org")
            self.assertEqual(host.host, "smtp.custom.org")
            self.assertEqual(host.port, 465)
            self.assertTrue(host.ssl)


class TestSrvLookup(TestCase):
    def test_srv_returns_none_without_dns(self):
        with patch("email_profile.providers._HAS_DNS", False):
            self.assertIsNone(_lookup_smtp_srv("example.com"))

    def test_srv_dns_exception_returns_none(self):
        from dns.exception import DNSException

        with (
            patch("email_profile.providers._HAS_DNS", True),
            patch(
                "email_profile.providers.dns.resolver.resolve",
                side_effect=DNSException(),
            ),
        ):
            self.assertIsNone(_lookup_smtp_srv("example.com"))

    def test_srv_port_465_marks_ssl(self):
        with (
            patch("email_profile.providers._HAS_DNS", True),
            patch(
                "email_profile.providers.dns.resolver.resolve",
                return_value=[_srv("mail.example.com.", 465)],
            ),
        ):
            host = _lookup_smtp_srv("example.com")
        self.assertEqual(host.host, "mail.example.com")
        self.assertEqual(host.port, 465)
        self.assertTrue(host.ssl)
        self.assertFalse(host.starttls)

    def test_srv_port_587_marks_starttls(self):
        with (
            patch("email_profile.providers._HAS_DNS", True),
            patch(
                "email_profile.providers.dns.resolver.resolve",
                return_value=[_srv("mail.example.com.", 587)],
            ),
        ):
            host = _lookup_smtp_srv("example.com")
        self.assertEqual(host.port, 587)
        self.assertFalse(host.ssl)
        self.assertTrue(host.starttls)


class TestMxLookup(TestCase):
    def test_mx_returns_none_without_dns(self):
        with patch("email_profile.providers._HAS_DNS", False):
            self.assertIsNone(_lookup_smtp_mx("example.com"))

    def test_mx_dns_exception_returns_none(self):
        from dns.exception import DNSException

        with (
            patch("email_profile.providers._HAS_DNS", True),
            patch(
                "email_profile.providers.dns.resolver.resolve",
                side_effect=DNSException(),
            ),
        ):
            self.assertIsNone(_lookup_smtp_mx("example.com"))

    def test_mx_hint_matches_to_smtp(self):
        with (
            patch("email_profile.providers._HAS_DNS", True),
            patch(
                "email_profile.providers.dns.resolver.resolve",
                return_value=[_mx("aspmx.l.google.com.")],
            ),
        ):
            host = _lookup_smtp_mx("example.com")
        self.assertEqual(host.host, "smtp.gmail.com")

    def test_mx_unmatched_hint_returns_none(self):
        with (
            patch("email_profile.providers._HAS_DNS", True),
            patch(
                "email_profile.providers.dns.resolver.resolve",
                return_value=[_mx("mx.totally-unknown-provider.io.")],
            ),
        ):
            self.assertIsNone(_lookup_smtp_mx("example.com"))


class TestResolutionOrder(TestCase):
    def test_known_provider_short_circuits_dns(self):
        with patch("email_profile.providers.dns.resolver.resolve") as resolver:
            resolve_smtp_host("user@gmail.com")
            resolver.assert_not_called()

    def test_srv_wins_over_mx_for_unknown_domain(self):
        def fake_resolve(name, rtype, lifetime=3.0):
            if rtype == "SRV":
                return [_srv("smtp.example.com.", 587)]
            raise AssertionError("MX must not be queried when SRV resolves")

        with (
            patch("email_profile.providers._HAS_DNS", True),
            patch(
                "email_profile.providers.dns.resolver.resolve",
                side_effect=fake_resolve,
            ),
        ):
            host = resolve_smtp_host("user@example.com")
        self.assertEqual(host.host, "smtp.example.com")
        self.assertEqual(host.port, 587)


class TestModuleSurface(TestCase):
    def test_smtp_mx_hints_populated(self):
        self.assertTrue(SMTP_MX_HINTS)
        for hint, smtp in SMTP_MX_HINTS:
            self.assertIsInstance(hint, str)
            self.assertTrue(smtp.host)

    def test_resolution_error_subclasses_runtime(self):
        self.assertTrue(issubclass(ProviderResolutionError, RuntimeError))
