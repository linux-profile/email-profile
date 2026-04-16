from unittest import TestCase
from unittest.mock import patch

from email_profile import Email
from tests.conftest import make_fake_client


class _WriteTest(TestCase):
    def setUp(self):
        self.fake = make_fake_client()
        self._patcher = patch(
            "email_profile.email.imaplib.IMAP4_SSL", return_value=self.fake
        )
        self._patcher.start()
        self.app = Email("imap.x", "u", "p").connect()

    def tearDown(self):
        self.app.close()
        self._patcher.stop()

    def _uid_calls_with(self, verb: str) -> list:
        return [
            c
            for c in self.fake.uid.call_args_list
            if c.args[0].upper() == verb
        ]


class TestFlagOperations(_WriteTest):
    def test_mark_seen_sends_plus_flags_seen(self):
        self.app.inbox.mark_seen("42")
        call = self._uid_calls_with("STORE")[0]
        self.assertEqual(call.args, ("STORE", "42", "+FLAGS", "\\Seen"))

    def test_mark_unseen_sends_minus_flags_seen(self):
        self.app.inbox.mark_unseen("42")
        call = self._uid_calls_with("STORE")[0]
        self.assertEqual(call.args, ("STORE", "42", "-FLAGS", "\\Seen"))

    def test_flag_and_unflag(self):
        self.app.inbox.flag("42")
        self.app.inbox.unflag("42")
        calls = self._uid_calls_with("STORE")
        self.assertEqual(calls[0].args, ("STORE", "42", "+FLAGS", "\\Flagged"))
        self.assertEqual(calls[1].args, ("STORE", "42", "-FLAGS", "\\Flagged"))


class TestDeleteExpunge(_WriteTest):
    def test_delete_marks_deleted(self):
        self.app.inbox.delete("42")
        call = self._uid_calls_with("STORE")[0]
        self.assertEqual(call.args, ("STORE", "42", "+FLAGS", "\\Deleted"))
        self.fake.expunge.assert_not_called()

    def test_delete_with_expunge_commits(self):
        self.app.inbox.delete("42", expunge=True)
        self.fake.expunge.assert_called_once()

    def test_undelete(self):
        self.app.inbox.undelete("42")
        call = self._uid_calls_with("STORE")[0]
        self.assertEqual(call.args, ("STORE", "42", "-FLAGS", "\\Deleted"))

    def test_expunge_standalone(self):
        self.app.inbox.expunge()
        self.fake.expunge.assert_called_once()


class TestCopyMove(_WriteTest):
    def test_copy_uses_uid_copy(self):
        self.app.inbox.copy("42", "Archive")
        call = self._uid_calls_with("COPY")[0]
        self.assertEqual(call.args, ("COPY", "42", "Archive"))

    def test_move_prefers_uid_move(self):
        self.app.inbox.move("42", "Archive")
        call = self._uid_calls_with("MOVE")[0]
        self.assertEqual(call.args, ("MOVE", "42", "Archive"))

    def test_move_falls_back_to_copy_delete(self):
        calls = []

        def fake_uid(command, *args):
            calls.append((command, args))
            if command.upper() == "MOVE":
                raise Exception("MOVE not supported")
            return ("OK", [b"Done"])

        self.fake.uid.side_effect = fake_uid
        self.app.inbox.move("42", "Archive")

        commands = [c[0].upper() for c in calls]
        self.assertIn("MOVE", commands)
        self.assertIn("COPY", commands)
        self.assertIn("STORE", commands)
        self.fake.expunge.assert_called_once()


class TestMailboxAdmin(_WriteTest):
    def test_create(self):
        self.app.inbox.create()
        self.fake.create.assert_called_once_with("INBOX")

    def test_delete_mailbox(self):
        self.app.inbox.delete_mailbox()
        self.fake.delete.assert_called_once_with("INBOX")

    def test_rename_to_updates_name(self):
        box = self.app.inbox
        box.rename_to("ARCHIVE")
        self.fake.rename.assert_called_once_with("INBOX", "ARCHIVE")
        self.assertEqual(box.name, "ARCHIVE")
