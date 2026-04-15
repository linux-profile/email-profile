from unittest.mock import patch

import pytest

from email_profile import Email, EmailSerializer, Storage
from email_profile.providers import (
    KNOWN_PROVIDERS,
    IMAPHost,
    resolve_imap_host,
)
from tests.conftest import SAMPLE_RFC822, make_fake_client

GMAIL_LIST = (
    b'(\\HasNoChildren) "/" "INBOX"',
    b'(\\HasChildren \\Noselect) "/" "[Gmail]"',
    b'(\\HasNoChildren) "/" "[Gmail]/Sent Mail"',
    b'(\\HasNoChildren) "/" "[Gmail]/Spam"',
    b'(\\HasNoChildren) "/" "[Gmail]/Trash"',
    b'(\\HasNoChildren) "/" "[Gmail]/Drafts"',
)


def _patched(client) -> Email:
    return Email(server="imap.example.com", user="u", password="p")


def test_known_provider_resolves_without_dns():
    host = resolve_imap_host("alice@gmail.com")
    assert host == KNOWN_PROVIDERS["gmail.com"]


def test_unknown_domain_falls_back_to_imap_dot_domain():
    with (
        patch("email_profile.providers._lookup_srv", return_value=None),
        patch("email_profile.providers._lookup_mx", return_value=None),
    ):
        host = resolve_imap_host("contato@suaempresa.com.br")
    assert host == IMAPHost("imap.suaempresa.com.br")


def test_srv_record_overrides_fallback():
    fake = IMAPHost("imap.real-host.example", port=993)
    with (
        patch("email_profile.providers._lookup_srv", return_value=fake),
        patch("email_profile.providers._lookup_mx", return_value=None),
    ):
        host = resolve_imap_host("user@anything.test")
    assert host == fake


def test_mx_hint_detects_hostinger():
    fake = IMAPHost("imap.hostinger.com")
    with (
        patch("email_profile.providers._lookup_srv", return_value=None),
        patch("email_profile.providers._lookup_mx", return_value=fake),
    ):
        host = resolve_imap_host("contato@suaempresa.com.br")
    assert host.host == "imap.hostinger.com"


def test_email_from_email_uses_resolver():
    with patch(
        "email_profile.email.resolve_imap_host",
        return_value=IMAPHost("imap.test.example", port=993),
    ):
        app = Email.from_email("alice@test.example", "pw")
    assert app._server == "imap.test.example"
    assert app._user == "alice@test.example"


def test_email_provider_factories():
    assert Email.gmail("u", "p")._server == "imap.gmail.com"
    assert Email.outlook("u", "p")._server == "outlook.office365.com"
    assert Email.icloud("u", "p")._server == "imap.mail.me.com"
    assert Email.yahoo("u", "p")._server == "imap.mail.yahoo.com"
    assert Email.hostinger("u", "p")._server == "imap.hostinger.com"
    assert Email.zoho("u", "p")._server == "imap.zoho.com"


def test_email_from_env_with_explicit_server(monkeypatch):
    monkeypatch.setenv("EMAIL_SERVER", "imap.x.com")
    monkeypatch.setenv("EMAIL_USERNAME", "u@x.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "pw")
    app = Email.from_env()
    assert app._server == "imap.x.com"


def test_email_from_env_auto_discovers_when_server_missing(monkeypatch):
    monkeypatch.delenv("EMAIL_SERVER", raising=False)
    monkeypatch.setenv("EMAIL_USERNAME", "alice@gmail.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "pw")
    app = Email.from_env()
    assert app._server == "imap.gmail.com"


def test_email_from_env_missing_credentials_raises(monkeypatch):
    monkeypatch.delenv("EMAIL_USERNAME", raising=False)
    monkeypatch.delenv("EMAIL_PASSWORD", raising=False)
    with pytest.raises(KeyError):
        Email.from_env(load_dotenv=False)


def test_inbox_property():
    fake = make_fake_client(mailboxes=GMAIL_LIST)
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
    ):
        assert app.inbox.name == "INBOX"


def test_sent_property_normalizes_gmail():
    fake = make_fake_client(mailboxes=GMAIL_LIST)
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
    ):
        assert "Sent" in app.sent.name


def test_spam_property_normalizes_gmail():
    fake = make_fake_client(mailboxes=GMAIL_LIST)
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
    ):
        assert "Spam" in app.spam.name


def test_trash_property_normalizes_gmail():
    fake = make_fake_client(mailboxes=GMAIL_LIST)
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
    ):
        assert "Trash" in app.trash.name


def test_drafts_property_normalizes_gmail():
    fake = make_fake_client(mailboxes=GMAIL_LIST)
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
    ):
        assert "Drafts" in app.drafts.name


def test_unread_shortcut_runs_query():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
    ):
        assert app.unread().count() >= 0
    search_calls = [
        c for c in fake.uid.call_args_list if c.args[0] == "search"
    ]
    assert any("(UNSEEN)" in str(c) for c in search_calls)


def test_recent_shortcut_passes_since():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
    ):
        app.recent(days=3).count()
    search_calls = [
        c for c in fake.uid.call_args_list if c.args[0] == "search"
    ]
    assert any("SINCE" in str(c) for c in search_calls)


def test_search_shortcut_uses_text_clause():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
    ):
        app.search("invoice").count()
    search_calls = [
        c for c in fake.uid.call_args_list if c.args[0] == "search"
    ]
    assert any("TEXT" in str(c) for c in search_calls)


def test_attachment_save(tmp_path):
    msg = EmailSerializer.from_raw(uid="1", mailbox="INBOX", raw=SAMPLE_RFC822)
    msg.attachments.append(
        type(msg)
        .model_fields["attachments"]
        .annotation.__args__[0](
            file_name="hello.txt",
            content_type="text/plain",
            content=b"hello world",
        )
    )
    out = msg.attachments[0].save(tmp_path)
    assert out.read_bytes() == b"hello world"


def test_msg_save_json_html(tmp_path):
    msg = EmailSerializer.from_raw(uid="1", mailbox="INBOX", raw=SAMPLE_RFC822)
    j = msg.save_json(tmp_path / "j")
    h = msg.save_html(tmp_path / "h")
    assert j.exists()
    assert h.exists()


def test_storage_accepts_plain_path(tmp_path):
    storage = Storage(tmp_path / "mail.db")
    assert "sqlite:///" in storage.url
    storage.dispose()


def test_storage_accepts_string_path(tmp_path):
    storage = Storage(str(tmp_path / "mail.db"))
    assert storage.url.startswith("sqlite:///")
    storage.dispose()
