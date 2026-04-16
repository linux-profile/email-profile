import tempfile
from pathlib import Path
from typing import Optional
from unittest import TestCase

from email_profile import StorageSQLite as Storage
from email_profile.core.abc import StorageABC
from email_profile.serializers.raw import RawSerializer


class _InMemoryStorage(StorageABC):
    """A minimal in-memory storage that inherits StorageABC."""

    def __init__(self) -> None:
        self._rows: dict[str, RawSerializer] = {}

    def save_raw(self, raw: RawSerializer) -> None:
        self._rows[raw.message_id] = raw

    def get_raw(self, message_id: str) -> Optional[RawSerializer]:
        return self._rows.get(message_id)

    def stored_ids(self) -> set[str]:
        return set(self._rows.keys())

    def stored_uids(self, mailbox: str) -> set[str]:
        return {r.uid for r in self._rows.values() if r.mailbox == mailbox}


class TestStorageABC(TestCase):
    def test_real_storage_satisfies_protocol(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage = Storage(Path(tmp) / "x.db")
            self.assertIsInstance(storage, StorageABC)

    def test_in_memory_satisfies_protocol(self):
        self.assertIsInstance(_InMemoryStorage(), StorageABC)

    def test_object_missing_methods_does_not_satisfy(self):
        class Partial:
            def save_raw(self, x):
                return x

        self.assertNotIsInstance(Partial(), StorageABC)


class TestInMemoryStorageRoundTrips(TestCase):
    def test_save_and_get(self):
        storage = _InMemoryStorage()
        raw = RawSerializer(
            message_id="<test@x>", uid="1", mailbox="INBOX", file="content"
        )

        storage.save_raw(raw)

        result = storage.get_raw("<test@x>")
        self.assertIsNotNone(result)
        self.assertEqual(result.message_id, "<test@x>")
