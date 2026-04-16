"""Minimal in-memory storage backend."""

from typing import Optional

from email_profile.advanced import StorageABC
from email_profile.serializers.raw import RawSerializer


class DictStorage(StorageABC):

    def __init__(self) -> None:
        self._data: dict[tuple[str, str], RawSerializer] = {}

    def save(self, raw: RawSerializer) -> bool:
        key = (raw.uid, raw.mailbox)

        if key in self._data:
            self._data[key] = raw
            return False

        self._data[key] = raw
        return True

    def get(self, message_id: str) -> Optional[RawSerializer]:
        for raw in self._data.values():
            if raw.message_id == message_id:
                return raw
        return None

    def ids(self, mailbox: Optional[str] = None) -> set[str]:
        return {
            raw.message_id
            for raw in self._data.values()
            if mailbox is None or raw.mailbox == mailbox
        }

    def uids(self, mailbox: str) -> set[str]:
        return {
            raw.uid
            for raw in self._data.values()
            if raw.mailbox == mailbox
        }
