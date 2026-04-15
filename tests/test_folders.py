from unittest import TestCase

from email_profile.folders import (
    INBOX_HINTS,
    SENT_HINTS,
    SPAM_HINTS,
    find_mailbox,
)


class TestFindMailbox(TestCase):

    def test_exact_match(self):
        result = find_mailbox({"INBOX": "x"}, INBOX_HINTS)
        self.assertEqual(result, "x")

    def test_substring_match(self):
        result = find_mailbox({"[Gmail]/Sent Mail": "y"}, SENT_HINTS)
        self.assertEqual(result, "y")

    def test_returns_none_when_no_match(self):
        self.assertIsNone(find_mailbox({"Foo": "z"}, INBOX_HINTS))

    def test_first_hint_wins(self):
        boxes = {"Junk": "j", "Spam": "s"}
        self.assertEqual(find_mailbox(boxes, SPAM_HINTS), "s")

    def test_localized_pt_name(self):
        self.assertEqual(
            find_mailbox({"Enviados": "x"}, SENT_HINTS), "x"
        )

    def test_case_insensitive(self):
        self.assertEqual(find_mailbox({"INBOX": "x"}, INBOX_HINTS), "x")
        self.assertEqual(find_mailbox({"inbox": "x"}, INBOX_HINTS), "x")
