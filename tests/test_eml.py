import tempfile
from pathlib import Path
from unittest import TestCase

from email_profile import EmailModel, EmailSerializer
from tests.conftest import SAMPLE_RFC822


class TestFromRaw(TestCase):
    def test_round_trips_basic_fields(self):
        msg = EmailSerializer.from_raw(
            uid="42", mailbox="INBOX", raw=SAMPLE_RFC822
        )
        self.assertEqual(msg.uid, "42")
        self.assertEqual(msg.mailbox, "INBOX")
        self.assertEqual(msg.subject, "Hello")

    def test_attaches_parsed_body(self):
        msg = EmailSerializer.from_raw(
            uid="1", mailbox="INBOX", raw=SAMPLE_RFC822
        )
        self.assertIn("Hi Bob", msg.body_text_plain)


class TestSaveMethods(TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.msg = EmailSerializer.from_raw(
            uid="1", mailbox="INBOX", raw=SAMPLE_RFC822
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_save_json(self):
        out = self.msg.save_json(self.tmp / "j")
        self.assertTrue(out.exists())

    def test_save_html(self):
        out = self.msg.save_html(self.tmp / "h")
        self.assertTrue(out.exists())

    def test_save_attachments_returns_paths(self):
        from email_profile import Attachment

        self.msg.attachments.append(
            Attachment(
                file_name="x.txt", content_type="text/plain", content=b"hi"
            )
        )
        paths = self.msg.save_attachments(self.tmp / "a")
        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0].read_bytes(), b"hi")


class TestEmailModel(TestCase):
    def test_from_serializer(self):
        msg = EmailSerializer.from_raw(
            uid="1", mailbox="INBOX", raw=SAMPLE_RFC822
        )
        model = EmailModel.from_serializer(msg)
        self.assertEqual(model.uid, "1")
        self.assertEqual(model.subject, "Hello")
