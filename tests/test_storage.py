import tempfile
from pathlib import Path
from unittest import TestCase

from email_profile import EmailSerializer, Storage
from tests.conftest import SAMPLE_RFC822


def _msg(uid: str = "1", mailbox: str = "INBOX") -> EmailSerializer:
    raw = SAMPLE_RFC822.replace(
        b"<abc@example.com>", f"<{uid}-{mailbox}@example.com>".encode()
    )
    return EmailSerializer.from_raw(uid=uid, mailbox=mailbox, raw=raw)


class TestStorageURL(TestCase):

    def test_accepts_plain_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage = Storage(Path(tmp) / "mail.db")
            self.assertIn("sqlite:///", storage.url)
            storage.dispose()

    def test_accepts_string_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage = Storage(f"{tmp}/mail.db")
            self.assertTrue(storage.url.startswith("sqlite:///"))
            storage.dispose()

    def test_accepts_full_url(self):
        storage = Storage("sqlite:///:memory:")
        self.assertEqual(storage.url, "sqlite:///:memory:")
        storage.dispose()


class TestStoragePersistence(TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(Path(self._tmp.name) / "mail.db")

    def tearDown(self):
        self.storage.dispose()
        self._tmp.cleanup()

    def test_save_one(self):
        self.storage.save(_msg("1"))
        self.assertEqual(len(list(self.storage.iter_messages())), 1)

    def test_save_many_returns_count(self):
        n = self.storage.save_many(iter([_msg("1"), _msg("2")]))
        self.assertEqual(n, 2)

    def test_iter_filters_by_mailbox(self):
        self.storage.save(_msg("1", "INBOX"))
        self.storage.save(_msg("2", "Sent"))
        self.assertEqual(
            {m.uid for m in self.storage.iter_messages(mailbox="INBOX")},
            {"1"},
        )


class TestStorageEmlIO(TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.storage = Storage(self.tmp / "src.db")
        self.storage.save(_msg("1", "INBOX"))
        self.storage.save(_msg("2", "Sent"))

    def tearDown(self):
        self.storage.dispose()
        self._tmp.cleanup()

    def test_export_writes_per_mailbox(self):
        n = self.storage.export_eml(self.tmp / "dump")
        self.assertEqual(n, 2)
        self.assertTrue((self.tmp / "dump" / "INBOX" / "1.eml").exists())
        self.assertTrue((self.tmp / "dump" / "Sent" / "2.eml").exists())

    def test_import_loads_back(self):
        self.storage.export_eml(self.tmp / "dump")

        dst = Storage(self.tmp / "dst.db")
        n = dst.import_eml(self.tmp / "dump")
        self.assertEqual(n, 2)
        self.assertEqual(
            {m.mailbox for m in dst.iter_messages()},
            {"INBOX", "Sent"},
        )
        dst.dispose()
