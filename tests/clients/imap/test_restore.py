"""Tests for Restore.restore_mailbox (single-mailbox path)."""

import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from email_profile import Email, StorageSQLite
from email_profile.clients.imap.restore import (
    Restore,
    _ensure_mailbox,
    _server_message_ids,
)
from email_profile.serializers.raw import RawSerializer
from tests.conftest import SAMPLE_RFC822, make_fake_client


def _save(storage: StorageSQLite, message_id: str, mailbox: str = "INBOX"):
    storage.save(
        RawSerializer(
            message_id=message_id,
            uid="1",
            mailbox=mailbox,
            file=SAMPLE_RFC822,
        )
    )


class _RestoreTest(TestCase):
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
        self.restore = Restore(self.app._session)

    def tearDown(self):
        self.app.close()
        self._patcher.stop()
        self._tmp.cleanup()


class TestRestoreMailbox(_RestoreTest):
    def test_uploads_new_message(self):
        _save(self.storage, "<abc@example.com>")
        # Server has no message_ids
        self.fake.uid.side_effect = lambda *_a, **_kw: ("OK", [b""])
        result = Restore.restore_mailbox(
            self.app._session,
            "INBOX",
            ["<abc@example.com>"],
            storage=self.storage,
        )
        self.assertEqual(result["uploaded"], 1)
        self.assertEqual(result["skipped"], 0)
        self.fake.append.assert_called_once()

    def test_skips_existing_message_ids(self):
        _save(self.storage, "<abc@example.com>")

        # Server returns the same message_id
        def side(command, *args):
            cmd = command.upper()
            if cmd == "SEARCH":
                return ("OK", [b"1"])
            if cmd == "FETCH":
                header = (
                    b"1 (UID 1 BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)] {%d}"
                    % len(SAMPLE_RFC822)
                )
                return ("OK", [(header, SAMPLE_RFC822), b")"])
            return ("OK", [b"Done"])

        self.fake.uid.side_effect = side

        result = Restore.restore_mailbox(
            self.app._session,
            "INBOX",
            ["<abc@example.com>"],
            storage=self.storage,
        )
        self.assertEqual(result["uploaded"], 0)
        self.assertEqual(result["skipped"], 1)
        self.fake.append.assert_not_called()

    def test_missing_storage_entry_dropped(self):
        # Storage has nothing for this id
        self.fake.uid.side_effect = lambda *_a, **_kw: ("OK", [b""])
        result = Restore.restore_mailbox(
            self.app._session,
            "INBOX",
            ["<missing@x>"],
            storage=self.storage,
        )
        self.assertEqual(result["uploaded"], 0)
        self.fake.append.assert_not_called()

    def test_skip_duplicates_disabled(self):
        _save(self.storage, "<abc@example.com>")
        # Even when server already has it, skip_duplicates=False uploads
        result = Restore.restore_mailbox(
            self.app._session,
            "INBOX",
            ["<abc@example.com>"],
            storage=self.storage,
            skip_duplicates=False,
        )
        self.assertEqual(result["uploaded"], 1)


class TestEnsureMailbox(_RestoreTest):
    def test_existing_mailbox_no_op(self):
        before = self.fake.create.call_count
        _ensure_mailbox(self.app._session, "INBOX")
        self.assertEqual(self.fake.create.call_count, before)

    def test_missing_mailbox_created(self):
        self.fake.list.return_value = (
            "OK",
            [
                b'(\\HasNoChildren) "/" "INBOX"',
                b'(\\HasNoChildren) "/" "Archive"',
            ],
        )
        _ensure_mailbox(self.app._session, "Archive")
        self.fake.create.assert_called_once()
        self.assertIn("Archive", self.app._session.mailboxes)


class TestServerMessageIds(_RestoreTest):
    def test_returns_empty_on_empty_search(self):
        self.fake.uid.side_effect = lambda *_a, **_kw: ("OK", [b""])
        ids = _server_message_ids(self.app._session.client, "INBOX")
        self.assertEqual(ids, set())
