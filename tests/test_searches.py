from unittest import TestCase
from unittest.mock import patch

from email_profile import Email
from tests.conftest import make_fake_client


class TestWhereLazy(TestCase):

    def setUp(self):
        self.fake = make_fake_client()
        self._patcher = patch(
            "email_profile.email.imaplib.IMAP4_SSL", return_value=self.fake
        )
        self._patcher.start()
        self.app = Email("imap.x", "u", "p").connect()

    def tearDown(self):
        self.app.close()
        self._patcher.stop()

    def test_count_does_not_fetch_bodies(self):
        n = self.app.inbox.where().count()
        self.assertEqual(n, 2)
        fetch_calls = [
            c for c in self.fake.uid.call_args_list if c.args[0] == "fetch"
        ]
        self.assertEqual(fetch_calls, [])

    def test_exists_short_circuits(self):
        self.assertTrue(self.app.inbox.where().exists())

    def test_uids(self):
        self.assertEqual(self.app.inbox.where().uids(), ["1", "2"])

    def test_first_returns_one(self):
        msg = self.app.inbox.where().first()
        self.assertIsNotNone(msg)
        self.assertEqual(msg.uid, "1")

    def test_iter_messages_yields(self):
        messages = list(self.app.inbox.where().iter_messages())
        self.assertEqual(len(messages), 1)

    def test_list_messages(self):
        self.assertEqual(len(self.app.inbox.where().list_messages()), 1)

    def test_independent_state_between_queries(self):
        first = self.app.inbox.where().list_messages()
        second = self.app.inbox.where().list_messages()
        self.assertIsNot(first, second)
