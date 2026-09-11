"""Which tools exist under which settings, and how the CLI maps to them."""

from __future__ import annotations

import asyncio

from email_profile.mcp.server import parse_args, settings_from_args
from tests.mcp.conftest import tool_names

READ_TOOLS = {
    "list_mailboxes",
    "search_messages",
    "read_message",
    "list_attachments",
    "save_attachment",
    "mark_seen",
    "mark_unseen",
    "flag_message",
    "unflag_message",
    "move_message",
}
SEND_TOOLS = {"send_email", "reply_message", "forward_message"}
DELETE_TOOLS = {"delete_message"}


def test_default_exposes_only_safe_tools(make_server):
    assert tool_names(make_server()) == READ_TOOLS


def test_allow_send_adds_smtp_tools(make_server):
    assert tool_names(make_server(allow_send=True)) == READ_TOOLS | SEND_TOOLS


def test_allow_delete_adds_delete_tool(make_server):
    names = tool_names(make_server(allow_delete=True))
    assert names == READ_TOOLS | DELETE_TOOLS


def test_annotations_mark_irreversible_tools(server):
    tools = {t.name: t.annotations for t in asyncio.run(server.list_tools())}
    assert tools["search_messages"].read_only_hint is True
    assert tools["mark_seen"].read_only_hint is False
    assert tools["mark_seen"].destructive_hint is False
    assert tools["send_email"].destructive_hint is True
    assert tools["send_email"].open_world_hint is True
    assert tools["delete_message"].destructive_hint is True


def test_every_tool_has_a_docstring(server):
    for tool in asyncio.run(server.list_tools()):
        assert tool.description, tool.name


def test_prompts_registered(server):
    names = {p.name for p in asyncio.run(server.list_prompts())}
    assert names == {
        "triage_inbox",
        "find_message",
        "draft_reply",
        "summarize_thread",
    }


def test_parse_args_defaults():
    args = parse_args([])
    assert args.allow_send is False
    assert args.allow_delete is False
    assert args.http is False
    assert args.max_chars is None


def test_settings_from_args_flags(monkeypatch):
    monkeypatch.delenv("EMAIL_MCP_ALLOW_SEND", raising=False)
    args = parse_args(["--allow-send", "--allow-delete", "--max-chars", "9"])
    settings = settings_from_args(args)
    assert settings.allow_send and settings.allow_delete
    assert settings.max_chars == 9


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("EMAIL_MCP_ALLOW_SEND", "true")
    monkeypatch.setenv("EMAIL_MCP_MAX_CHARS", "77")
    monkeypatch.setenv("EMAIL_MCP_DEFAULT_MAILBOX", "Work")
    monkeypatch.setenv("EMAIL_MCP_LIMIT", "50")
    monkeypatch.setenv("EMAIL_MCP_ATTACHMENTS_DIR", "/tmp/att")
    settings = settings_from_args(parse_args([]))
    assert settings.allow_send is True
    assert settings.allow_delete is False
    assert settings.max_chars == 77
    assert settings.default_mailbox == "Work"
    assert settings.limit == 50
    assert settings.attachments_dir == "/tmp/att"


def test_settings_limit_is_clamped(monkeypatch):
    monkeypatch.setenv("EMAIL_MCP_LIMIT", "9999")
    assert settings_from_args(parse_args([])).limit == 200
