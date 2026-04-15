from unittest import TestCase
from unittest.mock import patch

from email_profile import Email, EmailSerializer, Q, Query
from tests.conftest import SAMPLE_RFC822, make_fake_client


class TestMailBoxWhere(TestCase):

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

    def test_kwargs(self):
        w = self.app.inbox.where(subject="hi", unseen=True)
        self.assertIn("(SUBJECT", repr(w))
        self.assertIn("(UNSEEN)", repr(w))

    def test_q_expression(self):
        w = self.app.inbox.where(Q.subject("hi") & Q.unseen())
        self.assertIn("(SUBJECT", repr(w))

    def test_query_object(self):
        w = self.app.inbox.where(Query(subject="hi"))
        self.assertIn("(SUBJECT", repr(w))

    def test_query_and_kwargs_together_raises(self):
        with self.assertRaises(TypeError):
            self.app.inbox.where(Query(subject="x"), unseen=True)


class TestMailBoxAppend(TestCase):

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

    def test_calls_imap_append(self):
        msg = EmailSerializer.from_raw(
            uid="1", mailbox="INBOX", raw=SAMPLE_RFC822
        )
        self.app.inbox.append(msg)
        self.fake.append.assert_called_once()

    def test_accepts_bytes(self):
        self.app.inbox.append(SAMPLE_RFC822)
        self.assertEqual(self.fake.append.call_count, 1)

    def test_accepts_str(self):
        self.app.inbox.append(SAMPLE_RFC822.decode())
        self.assertEqual(self.fake.append.call_count, 1)

    def test_rejects_unsupported_type(self):
        with self.assertRaises(TypeError):
            self.app.inbox.append(42)
