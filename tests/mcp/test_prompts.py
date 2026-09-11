"""Prompts name the tools they lead to, in order."""

from __future__ import annotations

import asyncio


def _text(server, name: str, **args) -> str:
    result = asyncio.run(server.get_prompt(name, args))
    return "\n".join(m.content.text for m in result.messages)


def test_triage_uses_unseen_search(server):
    text = _text(server, "triage_inbox", mailbox="Work", limit="5")
    assert "search_messages" in text
    assert "mailbox=Work" in text
    assert "unseen=true" in text


def test_draft_reply_requires_approval_before_sending(server):
    text = _text(server, "draft_reply", mailbox="INBOX", uid="3")
    assert text.index("read_message") < text.index("reply_message")
    assert "approval" in text


def test_draft_reply_without_uid_searches_first(server):
    text = _text(server, "draft_reply")
    assert "search_messages" in text


def test_find_message_asks_when_query_missing(server):
    assert "ask the user" in _text(server, "find_message")


def test_summarize_thread_reads_oldest_first(server):
    text = _text(server, "summarize_thread", subject="Q3")
    assert "oldest to newest" in text
