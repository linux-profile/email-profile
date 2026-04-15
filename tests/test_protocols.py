import tempfile
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Optional
from unittest import TestCase

from email_profile import EmailSerializer, Storage, StorageProtocol
from tests.conftest import SAMPLE_RFC822


class _InMemoryStorage:
    """A minimal storage that satisfies StorageProtocol without subclassing."""

    def __init__(self) -> None:
        self._rows: list[EmailSerializer] = []

    def save(self, serializer: EmailSerializer) -> EmailSerializer:
        self._rows.append(serializer)
        return serializer

    def save_many(
        self,
        serializers: Iterable[EmailSerializer],
        *,
        batch_size: Optional[int] = None,
    ) -> int:
        count = 0
        for s in serializers:
            self._rows.append(s)
            count += 1
        return count

    def messages(
        self, mailbox: Optional[str] = None
    ) -> Iterator[EmailSerializer]:
        for row in self._rows:
            if mailbox is None or row.mailbox == mailbox:
                yield row

    def existing_ids(self, mailbox: Optional[str] = None) -> set[str]:
        return {
            r.id
            for r in self._rows
            if r.id and (mailbox is None or r.mailbox == mailbox)
        }

    def existing_uids(self, mailbox: str) -> set[str]:
        return {r.uid for r in self._rows if r.mailbox == mailbox}

    def dispose(self) -> None:
        self._rows.clear()


class TestStorageProtocol(TestCase):
    def test_real_storage_satisfies_protocol(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage = Storage(Path(tmp) / "x.db")
            self.assertIsInstance(storage, StorageProtocol)
            storage.dispose()

    def test_in_memory_satisfies_protocol(self):
        self.assertIsInstance(_InMemoryStorage(), StorageProtocol)

    def test_object_missing_methods_does_not_satisfy(self):
        class Partial:
            def save(self, x):
                return x

        self.assertNotIsInstance(Partial(), StorageProtocol)


class TestInMemoryStorageRoundTrips(TestCase):
    def test_save_and_messages(self):
        storage = _InMemoryStorage()
        msg = EmailSerializer.from_raw(
            uid="1", mailbox="INBOX", raw=SAMPLE_RFC822
        )

        storage.save(msg)

        out = list(storage.messages())
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].uid, "1")
