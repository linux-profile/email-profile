from unittest import TestCase

from email_profile import QuotaExceeded, RateLimited
from email_profile.core.status import IMAPError, Status


class TestStatus(TestCase):
    def test_validate_status_ok(self):
        response = Status.validate_status("OK")
        self.assertTrue(response.ok)
        self.assertTrue(response.type)

    def test_validate_status_no_raises(self):
        with self.assertRaises(IMAPError):
            Status.validate_status("NO")

    def test_validate_status_bad_raises(self):
        with self.assertRaises(IMAPError):
            Status.validate_status("BAD")

    def test_validate_status_unknown_raises(self):
        with self.assertRaises(IMAPError):
            Status.validate_status("XYZ")

    def test_validate_status_no_raise_returns_response(self):
        response = Status.validate_status("NO", raise_error=False)
        self.assertFalse(response.ok)


class TestValidateData(TestCase):
    def test_decodes_uids(self):
        self.assertEqual(Status.validate_data([b"1 2 3"]), ["1", "2", "3"])

    def test_handles_empty(self):
        self.assertEqual(Status.validate_data([b""]), [])
        self.assertEqual(Status.validate_data([]), [])


class TestClassifyPayload(TestCase):
    def test_overquota_raises_quota(self):
        with self.assertRaises(QuotaExceeded):
            Status.validate_status("NO", payload=[b"[OVERQUOTA] mailbox full"])

    def test_bandwidth_limit_raises_rate(self):
        with self.assertRaises(RateLimited):
            Status.validate_status(
                "NO", payload=[b"[BANDWIDTH-LIMIT] try later"]
            )

    def test_too_many_raises_rate(self):
        with self.assertRaises(RateLimited):
            Status.validate_status("NO", payload=[b"[TOO MANY] connections"])

    def test_generic_no_still_raises_imap_error(self):
        with self.assertRaises(IMAPError):
            Status.validate_status("NO", payload=[b"login failed"])
