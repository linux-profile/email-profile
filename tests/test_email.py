from unittest.mock import patch

import pytest

from email_profile import Email, NotConnected, Q, Query, Storage
from tests.conftest import make_fake_client


def _patched_email(client) -> Email:
    patcher = patch(
        "email_profile.email.imaplib.IMAP4_SSL", return_value=client
    )
    patcher.start()
    return Email(server="imap.example.com", user="u", password="p")


def test_email_does_not_connect_eagerly():
    fake = make_fake_client()
    with patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake):
        Email(server="imap.example.com", user="u", password="p")
    fake.login.assert_not_called()


def test_mailbox_requires_connection():
    fake = make_fake_client()
    app = _patched_email(fake)
    with pytest.raises(NotConnected):
        app.mailbox("INBOX")


def test_context_manager_connects_and_closes():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email(server="imap.example.com", user="u", password="p") as app,
    ):
        assert "INBOX" in app.mailboxes()
    fake.login.assert_called_once()
    fake.logout.assert_called_once()


def test_unknown_mailbox_raises():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email(server="imap.example.com", user="u", password="p") as app,
        pytest.raises(KeyError),
    ):
        app.mailbox("Trash")


def test_where_returns_independent_results():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email(server="imap.example.com", user="u", password="p") as app,
    ):
        inbox = app.mailbox("INBOX")
        first = inbox.where(Query(subject="hello")).list_messages()
        second = inbox.where(Query(subject="hello")).list_messages()
    assert len(first) == len(second)
    assert first is not second


def test_iter_messages_is_lazy():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email(server="imap.example.com", user="u", password="p") as app,
    ):
        it = app.mailbox("INBOX").where().iter_messages()
        first = next(it)
    assert first.mailbox == "INBOX"
    assert first.from_ == "alice@example.com"


def test_storage_save_persists_message(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'mail.db'}"
    storage = Storage(url=db_url)
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email(server="imap.example.com", user="u", password="p") as app,
    ):
        messages = app.mailbox("INBOX").where().list_messages()
        for msg in messages:
            storage.save(msg)
    assert len(messages) >= 1
    storage.dispose()


def test_storage_save_many_returns_count(tmp_path):
    storage = Storage(url=f"sqlite:///{tmp_path / 'm.db'}")
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email(server="imap.example.com", user="u", password="p") as app,
    ):
        saved = storage.save_many(app.mailbox("INBOX").where().iter_messages())
    assert saved >= 1
    storage.dispose()


def test_count_does_not_fetch_bodies():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email(server="imap.example.com", user="u", password="p") as app,
    ):
        n = app.mailbox("INBOX").where().count()
    assert n == 2
    fetch_calls = [c for c in fake.uid.call_args_list if c.args[0] == "fetch"]
    assert fetch_calls == []


def test_exists_short_circuits():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email(server="imap.example.com", user="u", password="p") as app,
    ):
        assert app.mailbox("INBOX").where().exists() is True


def test_where_accepts_kwargs():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email(server="imap.example.com", user="u", password="p") as app,
    ):
        w = app.mailbox("INBOX").where(subject="hi", unseen=True)
    assert "(SUBJECT" in repr(w)
    assert "(UNSEEN)" in repr(w)


def test_where_rejects_query_and_kwargs_together():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email(server="imap.example.com", user="u", password="p") as app,
        pytest.raises(TypeError),
    ):
        app.mailbox("INBOX").where(Query(subject="x"), unseen=True)


def test_where_accepts_q_expression():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email(server="imap.example.com", user="u", password="p") as app,
    ):
        w = app.mailbox("INBOX").where(Q.subject("hi") & Q.unseen())
    assert "(SUBJECT" in repr(w)
    assert "(UNSEEN)" in repr(w)


def test_first_returns_one_message_or_none():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email(server="imap.example.com", user="u", password="p") as app,
    ):
        msg = app.mailbox("INBOX").where().first()
    assert msg is not None
    assert msg.uid == "1"
