from unittest.mock import patch

import pytest

from email_profile import Email, EmailSerializer, Storage
from tests.conftest import SAMPLE_RFC822, make_fake_client


def _msg(uid: str = "1", mailbox: str = "INBOX") -> EmailSerializer:
    raw = SAMPLE_RFC822.replace(
        b"<abc@example.com>", f"<{uid}-{mailbox}@example.com>".encode()
    )
    return EmailSerializer.from_raw(uid=uid, mailbox=mailbox, raw=raw)


def test_mailbox_append_calls_imap_append():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
    ):
        app.inbox.append(_msg())
    assert fake.append.called
    args, _ = fake.append.call_args
    assert args[0] == "INBOX"
    assert SAMPLE_RFC822.startswith(b"Message-ID")


def test_mailbox_append_accepts_bytes_and_str():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
    ):
        app.inbox.append(SAMPLE_RFC822)
        app.inbox.append(SAMPLE_RFC822.decode())
    assert fake.append.call_count == 2


def test_mailbox_append_rejects_unsupported_type():
    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
        pytest.raises(TypeError),
    ):
        app.inbox.append(42)


def test_storage_iter_messages_round_trips(tmp_path):
    storage = Storage(tmp_path / "mail.db")
    storage.save(_msg("1"))
    storage.save(_msg("2"))

    out = list(storage.iter_messages())
    assert len(out) == 2
    assert {m.uid for m in out} == {"1", "2"}
    storage.dispose()


def test_storage_iter_messages_filters_by_mailbox(tmp_path):
    storage = Storage(tmp_path / "mail.db")
    storage.save(_msg("1", "INBOX"))
    storage.save(_msg("2", "Sent"))

    inbox = list(storage.iter_messages(mailbox="INBOX"))
    assert {m.uid for m in inbox} == {"1"}
    storage.dispose()


def test_storage_export_eml_writes_files(tmp_path):
    storage = Storage(tmp_path / "mail.db")
    storage.save(_msg("1", "INBOX"))
    storage.save(_msg("2", "Sent"))

    out = tmp_path / "dump"
    n = storage.export_eml(out)

    assert n == 2
    assert (out / "INBOX" / "1.eml").exists()
    assert (out / "Sent" / "2.eml").exists()
    assert b"From: Alice" in (out / "INBOX" / "1.eml").read_bytes()
    storage.dispose()


def test_storage_import_eml_loads_back(tmp_path):
    src = Storage(tmp_path / "src.db")
    src.save(_msg("1", "INBOX"))
    src.save(_msg("2", "Sent"))
    src.export_eml(tmp_path / "dump")
    src.dispose()

    dst = Storage(tmp_path / "dst.db")
    n = dst.import_eml(tmp_path / "dump")

    assert n == 2
    rows = list(dst.iter_messages())
    assert len(rows) == 2
    assert {r.mailbox for r in rows} == {"INBOX", "Sent"}
    dst.dispose()


def test_email_restore_re_uploads_to_server(tmp_path):
    storage = Storage(tmp_path / "src.db")
    storage.save(_msg("1", "INBOX"))
    storage.save(_msg("2", "INBOX"))

    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
    ):
        n = app.restore(storage)

    assert n == 2
    assert fake.append.call_count == 2
    storage.dispose()


def test_email_restore_unknown_mailbox_raises(tmp_path):
    storage = Storage(tmp_path / "src.db")
    storage.save(_msg("1", "Archive"))

    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
        pytest.raises(KeyError),
    ):
        app.restore(storage)
    storage.dispose()


def test_email_restore_with_target_overrides_mailbox(tmp_path):
    storage = Storage(tmp_path / "src.db")
    storage.save(_msg("1", "Archive"))

    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
    ):
        n = app.restore(storage, target="INBOX")

    assert n == 1
    args, _ = fake.append.call_args
    assert args[0] == "INBOX"
    storage.dispose()


def test_email_restore_eml_from_directory(tmp_path):
    box = tmp_path / "INBOX"
    box.mkdir()
    (box / "1.eml").write_bytes(SAMPLE_RFC822)
    (box / "2.eml").write_bytes(SAMPLE_RFC822)

    fake = make_fake_client()
    with (
        patch("email_profile.email.imaplib.IMAP4_SSL", return_value=fake),
        Email("imap.x", "u", "p") as app,
    ):
        n = app.restore_eml(tmp_path)

    assert n == 2
    assert fake.append.call_count == 2
