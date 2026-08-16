from unittest import TestCase

from email_profile.models.raw import RawModel
from email_profile.serializers.email import Message
from email_profile.serializers.raw import RawSerializer
from tests.conftest import SAMPLE_RFC822


class TestFromRaw(TestCase):
    def test_round_trips_basic_fields(self):
        msg = Message.from_raw(uid="42", mailbox="INBOX", raw=SAMPLE_RFC822)
        self.assertEqual(msg.uid, "42")
        self.assertEqual(msg.mailbox, "INBOX")
        self.assertEqual(msg.subject, "Hello")

    def test_attaches_parsed_body(self):
        msg = Message.from_raw(uid="1", mailbox="INBOX", raw=SAMPLE_RFC822)
        self.assertIn("Hi Bob", msg.body_text_plain)


class TestRawSerializer(TestCase):
    def test_creates_from_fields(self):
        raw = RawSerializer(
            message_id="<abc@x>", uid="1", mailbox="INBOX", file=b"raw content"
        )
        self.assertEqual(raw.message_id, "<abc@x>")
        self.assertEqual(raw.file, b"raw content")

    def test_str_input_coerced_to_bytes_latin1(self):
        raw = RawSerializer(
            message_id="<x>", uid="1", mailbox="INBOX", file="hello"
        )
        self.assertEqual(raw.file, b"hello")

    def test_bytes_preserved_verbatim(self):
        payload = bytes(range(256))
        raw = RawSerializer(
            message_id="<x>", uid="1", mailbox="INBOX", file=payload
        )
        self.assertEqual(raw.file, payload)


class TestRawModel(TestCase):
    def test_tablename(self):
        self.assertEqual(RawModel.__tablename__, "raw")

    def test_has_message_id_column(self):
        self.assertIn("message_id", RawModel.__table__.columns.keys())
