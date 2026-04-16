from unittest import TestCase

from email_profile import ConnectionFailure, NotConnected


class TestErrors(TestCase):
    def test_connection_failure_message(self):
        self.assertIn("Failed to connect", str(ConnectionFailure()))

    def test_not_connected_message(self):
        self.assertIn("not connected", str(NotConnected()))
