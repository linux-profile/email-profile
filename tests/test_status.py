from unittest import TestCase

from email_profile import IMAPError, Status


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
