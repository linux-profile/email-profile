"""Tool behaviour over the fake IMAP client."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest

from tests.mcp.conftest import call


def test_list_mailboxes(server):
    assert call(server, "list_mailboxes") == ["INBOX", "Sent"]


def test_search_returns_headers_only(server):
    page = call(server, "search_messages", mailbox="INBOX", limit=5)
    assert page["total"] == 2
    assert page["next_offset"] is None
    row = page["messages"][0]
    assert row["subject"] == "Hello"
    assert row["from"] == "alice@example.com"
    assert "body" not in row


def test_search_by_sender(server, fake_client):
    call(server, "search_messages", sender="alice")
    searches = [
        c.args for c in fake_client.uid.call_args_list if c.args[0] == "search"
    ]
    assert any('FROM "alice"' in " ".join(map(str, c)) for c in searches)


def test_search_pages_past_the_end(server):
    page = call(server, "search_messages", offset=5, limit=5)
    assert page["total"] == 2
    assert page["messages"] == []


def test_search_reports_next_offset(server):
    page = call(server, "search_messages", limit=1)
    assert page["next_offset"] == 1


def test_search_rejects_limit_above_cap(server):
    with pytest.raises(Exception, match="limit"):
        asyncio.run(server.call_tool("search_messages", {"limit": 10_000}))


def test_read_message_truncates(server):
    detail = call(
        server, "read_message", mailbox="INBOX", uid="1", max_chars=3
    )
    assert detail["truncated"] is True
    assert "[truncated" in detail["body"]
    assert detail["attachment_list"] == []


def test_read_message_uses_server_default(make_server):
    server = make_server(max_chars=2)
    detail = call(server, "read_message", mailbox="INBOX", uid="1")
    assert detail["truncated"] is True


def test_read_message_zero_disables_truncation(make_server):
    server = make_server(max_chars=2)
    detail = call(
        server, "read_message", mailbox="INBOX", uid="1", max_chars=0
    )
    assert detail["truncated"] is False
    assert detail["body"] == "Hi Bob."


def test_read_message_missing_uid_is_a_tool_error(server, fake_client):
    fake_client.uid.side_effect = lambda *_: ("OK", [b""])
    with pytest.raises(Exception, match="No message with uid='9'"):
        asyncio.run(
            server.call_tool("read_message", {"mailbox": "INBOX", "uid": "9"})
        )


def test_save_attachment_missing_name(server):
    with pytest.raises(Exception, match="No attachment named 'x.pdf'"):
        asyncio.run(
            server.call_tool(
                "save_attachment",
                {"mailbox": "INBOX", "uid": "1", "file_name": "x.pdf"},
            )
        )


@pytest.mark.parametrize(
    "tool", ["mark_seen", "mark_unseen", "flag_message", "unflag_message"]
)
def test_flag_tools_issue_store(server, fake_client, tool):
    outcome = call(server, tool, mailbox="INBOX", uid="1")
    assert outcome["ok"] is True
    assert outcome["uid"] == "1"
    commands = [c.args[0].upper() for c in fake_client.uid.call_args_list]
    assert "STORE" in commands


def test_move_message(server, fake_client):
    outcome = call(
        server, "move_message", mailbox="INBOX", uid="1", destination="Sent"
    )
    assert outcome["detail"] == "Sent"
    commands = [c.args[0].upper() for c in fake_client.uid.call_args_list]
    assert "MOVE" in commands or "COPY" in commands


def test_delete_flags_without_expunge(server, fake_client):
    outcome = call(server, "delete_message", mailbox="INBOX", uid="1")
    assert outcome["detail"] == "flagged"
    fake_client.expunge.assert_not_called()


def test_delete_with_expunge(server, fake_client):
    outcome = call(
        server, "delete_message", mailbox="INBOX", uid="1", expunge=True
    )
    assert outcome["detail"] == "expunged"
    fake_client.expunge.assert_called_once()


def test_send_email_splits_recipients(server, app):
    with patch.object(app, "send") as send:
        outcome = call(
            server,
            "send_email",
            to="bob@example.com, eve@example.com",
            subject="Hi",
            body="x",
            cc=["c@example.com"],
        )
    assert outcome["action"] == "send"
    kwargs = send.call_args.kwargs
    assert kwargs["to"] == ["bob@example.com", "eve@example.com"]
    assert kwargs["cc"] == ["c@example.com"]
    assert kwargs["bcc"] is None


def test_reply_uses_original_message(server, app):
    with patch.object(app, "reply") as reply:
        call(server, "reply_message", mailbox="INBOX", uid="1", body="ok")
    original = reply.call_args.args[0]
    assert original.subject == "Hello"
    assert reply.call_args.kwargs["reply_all"] is False


def test_forward_uses_original_message(server, app):
    with patch.object(app, "forward") as forward:
        call(server, "forward_message", mailbox="INBOX", uid="1", to="x@y.z")
    assert forward.call_args.kwargs["to"] == ["x@y.z"]


def test_session_connects_lazily(app):
    from email_profile.mcp import Settings, build

    calls = []

    def factory():
        calls.append(1)
        return app

    server = build(Settings(), email_factory=factory)
    assert calls == []
    call(server, "list_mailboxes")
    call(server, "list_mailboxes")
    assert calls == [1]


def test_uid_rejects_sequence_sets(server):
    with pytest.raises(Exception, match="uid"):
        asyncio.run(
            server.call_tool("mark_seen", {"mailbox": "INBOX", "uid": "1:*"})
        )


def test_delete_rejects_uid_list(server, fake_client):
    with pytest.raises(Exception, match="uid"):
        asyncio.run(
            server.call_tool(
                "delete_message",
                {"mailbox": "INBOX", "uid": "1,2", "expunge": True},
            )
        )
    fake_client.expunge.assert_not_called()


def test_search_escapes_quotes(server, fake_client):
    call(server, "search_messages", subject='foo" UNSEEN "')
    searches = [
        " ".join(map(str, c.args))
        for c in fake_client.uid.call_args_list
        if c.args[0] == "search"
    ]
    assert any('SUBJECT "foo\\" UNSEEN \\""' in s for s in searches)


def test_save_attachment_refuses_paths_outside_root(app, tmp_path):
    from email_profile.mcp import Settings, build

    server = build(
        Settings(attachments_dir=str(tmp_path)), email_factory=lambda: app
    )
    for directory in ("..", "/etc", "../../x"):
        with pytest.raises(Exception, match="outside the attachments root"):
            asyncio.run(
                server.call_tool(
                    "save_attachment",
                    {
                        "mailbox": "INBOX",
                        "uid": "1",
                        "file_name": "a.pdf",
                        "directory": directory,
                    },
                )
            )


def test_confine_allows_subdirectories(tmp_path):
    from email_profile.mcp.tools.message import _confine

    assert (
        _confine(str(tmp_path), "inbox/2026")
        == (tmp_path / "inbox" / "2026").resolve()
    )
    assert _confine(str(tmp_path), ".") == tmp_path.resolve()


def test_tools_serialize_on_the_session_lock(app):
    import threading

    from email_profile.mcp import Settings, build

    calls = []

    def factory():
        calls.append(threading.get_ident())
        return app

    server = build(Settings(), email_factory=factory)
    threads = [
        threading.Thread(target=call, args=(server, "list_mailboxes"))
        for _ in range(8)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(calls) == 1
