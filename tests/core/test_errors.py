from unittest import TestCase

from email_profile import ConnectionFailure, NotConnected


class TestErrors(TestCase):
    def test_connection_failure_message(self):
        self.assertIn("Failed to connect", str(ConnectionFailure()))

    def test_not_connected_message(self):
        self.assertIn("not connected", str(NotConnected()))

    def test_connection_failure_names_host_and_cause(self):
        error = ConnectionFailure("imap.x", 993, OSError("timed out"))
        self.assertIn("imap.x:993", str(error))
        self.assertIn("OSError: timed out", str(error))
