from unittest import TestCase

from email_profile.models.raw import RawModel
from email_profile.serializers.email import EmailSerializer
from email_profile.serializers.raw import RawSerializer
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


class TestRawSerializer(TestCase):
    def test_creates_from_fields(self):
        raw = RawSerializer(
            message_id="<abc@x>", uid="1", mailbox="INBOX", file="raw content"
        )
        self.assertEqual(raw.message_id, "<abc@x>")
        self.assertEqual(raw.file, "raw content")


class TestRawModel(TestCase):
    def test_tablename(self):
        self.assertEqual(RawModel.__tablename__, "raw")

    def test_has_message_id_column(self):
        self.assertIn("message_id", RawModel.__table__.columns.keys())
