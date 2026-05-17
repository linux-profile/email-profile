"""Tests for Sync.sync (single-mailbox path)."""

import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from email_profile import Email, StorageSQLite
from email_profile.clients.imap.sync import Sync
from tests.conftest import SAMPLE_RFC822, make_fake_client


def _fetch_uid_search(uids: list[bytes]) -> dict[str, object]:
    """A fake uid() that returns the given UIDs to SEARCH and bodies to FETCH."""
    return list(uids)


class _SyncTest(TestCase):
    def setUp(self):
        self.fake = make_fake_client()
        self._patcher = patch(
            "email_profile.clients.imap.client.imaplib.IMAP4_SSL",
            return_value=self.fake,
        )
        self._patcher.start()
        self.app = Email("imap.x", "u", "p").connect()

        self._tmp = tempfile.TemporaryDirectory()
        self.storage = StorageSQLite(Path(self._tmp.name) / "mail.db")
        self.sync = Sync(self.app._session)

    def tearDown(self):
        self.app.close()
        self._patcher.stop()
        self._tmp.cleanup()


class TestSyncSingleMailbox(_SyncTest):
    def test_inserts_new_messages(self):
        # Wire up UID SEARCH → [1], UID FETCH → SAMPLE_RFC822
        def side(command, *args):
            cmd = command.upper()
            if cmd == "SEARCH":
                return ("OK", [b"1"])
            if cmd == "FETCH":
                header = b"1 (UID 1 FLAGS (\\Seen) RFC822 {%d}" % len(
                    SAMPLE_RFC822
                )
                return ("OK", [(header, SAMPLE_RFC822), b")"])
            return ("OK", [b"Done"])

        self.fake.uid.side_effect = side

        result = self.sync.sync(self.app.inbox, self.storage)
        self.assertEqual(result.inserted, 1)
        self.assertEqual(result.updated, 0)
        self.assertEqual(result.skipped, 0)
        self.assertFalse(result.has_errors)

    def test_skips_duplicate_message_ids(self):
        def side(command, *args):
            cmd = command.upper()
            if cmd == "SEARCH":
                return ("OK", [b"1"])
            if cmd == "FETCH":
                header = b"1 (UID 1 FLAGS () RFC822 {%d}" % len(SAMPLE_RFC822)
                return ("OK", [(header, SAMPLE_RFC822), b")"])
            return ("OK", [b"Done"])

        self.fake.uid.side_effect = side
        # First sync stores the message
        first = self.sync.sync(self.app.inbox, self.storage)
        self.assertEqual(first.inserted, 1)
        # Second sync sees the same message-id and skips
        second = self.sync.sync(self.app.inbox, self.storage)
        self.assertEqual(second.inserted, 0)
        self.assertEqual(second.skipped, 1)

    def test_empty_mailbox_no_work(self):
        def side(command, *args):
            if command.upper() == "SEARCH":
                return ("OK", [b""])
            return ("OK", [b"Done"])

        self.fake.uid.side_effect = side
        result = self.sync.sync(self.app.inbox, self.storage)
        self.assertEqual(result.inserted, 0)
        self.assertEqual(result.updated, 0)
        self.assertEqual(result.skipped, 0)

    def test_progress_callback_invoked(self):
        def side(command, *args):
            cmd = command.upper()
            if cmd == "SEARCH":
                return ("OK", [b"1"])
            if cmd == "FETCH":
                header = b"1 (UID 1 FLAGS () RFC822 {%d}" % len(SAMPLE_RFC822)
                return ("OK", [(header, SAMPLE_RFC822), b")"])
            return ("OK", [b"Done"])

        self.fake.uid.side_effect = side

        events: list[tuple[int, int]] = []
        self.sync.sync(
            self.app.inbox,
            self.storage,
            on_progress=lambda done, total: events.append((done, total)),
        )
        self.assertTrue(events)
        self.assertEqual(events[-1][0], events[-1][1])

    def test_storage_save_failure_recorded_as_error(self):
        def side(command, *args):
            cmd = command.upper()
            if cmd == "SEARCH":
                return ("OK", [b"1"])
            if cmd == "FETCH":
                header = b"1 (UID 1 FLAGS () RFC822 {%d}" % len(SAMPLE_RFC822)
                return ("OK", [(header, SAMPLE_RFC822), b")"])
            return ("OK", [b"Done"])

        self.fake.uid.side_effect = side

        with patch.object(
            self.storage, "save", side_effect=RuntimeError("disk full")
        ):
            result = self.sync.sync(self.app.inbox, self.storage)

        self.assertTrue(result.has_errors)
        self.assertEqual(result.inserted, 0)
