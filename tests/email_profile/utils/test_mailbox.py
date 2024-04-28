from email_profile.utils import Mailbox


def test_mainbox_inbox():
    assert Mailbox.INBOX == 'INBOX'


def test_mainbox_sent():
    assert Mailbox.SENT == 'INBOX.Sent'


def test_mainbox_junk():
    assert Mailbox.JUNK == 'INBOX.Junk'


def test_mainbox_drafts():
    assert Mailbox.DRAFTS == 'INBOX.Drafts'
