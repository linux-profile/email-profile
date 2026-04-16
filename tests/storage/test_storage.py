import tempfile
from pathlib import Path
from unittest import TestCase

from email_profile import StorageSQLite as Storage
from email_profile.serializers.raw import RawSerializer


def _raw(
    message_id: str = "<test@x>",
    uid: str = "1",
    mailbox: str = "INBOX",
    file_content: str = "raw content",
) -> RawSerializer:
    return RawSerializer(
        message_id=message_id, uid=uid, mailbox=mailbox, file=file_content
    )


class TestStorageURL(TestCase):
    def test_accepts_plain_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage = Storage(Path(tmp) / "mail.db")
            self.assertIn("sqlite:///", storage.url)

    def test_accepts_string_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage = Storage(f"{tmp}/mail.db")
            self.assertTrue(storage.url.startswith("sqlite:///"))

    def test_accepts_full_url(self):
        storage = Storage("sqlite:///:memory:")
        self.assertEqual(storage.url, "sqlite:///:memory:")


class TestStorageRaw(TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(Path(self._tmp.name) / "mail.db")

    def tearDown(self):
        self._tmp.cleanup()

    def test_save_and_get(self):
        raw = _raw("<test@x>")
        self.storage.save(raw)
        result = self.storage.get("<test@x>")
        self.assertIsNotNone(result)
        self.assertEqual(result.message_id, "<test@x>")
        self.assertEqual(result.file, "raw content")

    def test_get_returns_none_for_missing(self):
        result = self.storage.get("nonexistent")
        self.assertIsNone(result)

    def test_save_upserts(self):
        self.storage.save(_raw("<x@x>", file_content="v1"))
        self.storage.save(_raw("<x@x>", file_content="v2"))
        result = self.storage.get("<x@x>")
        self.assertEqual(result.file, "v2")

    def test_ids(self):
        self.storage.save(_raw("<a@x>"))
        self.storage.save(_raw("<b@x>", uid="2"))
        ids = self.storage.ids()
        self.assertEqual(ids, {"<a@x>", "<b@x>"})

    def test_uids(self):
        self.storage.save(_raw("<a@x>", uid="10", mailbox="INBOX"))
        self.storage.save(_raw("<b@x>", uid="20", mailbox="Sent"))
        self.assertEqual(self.storage.uids("INBOX"), {"10"})
        self.assertEqual(self.storage.uids("Sent"), {"20"})
