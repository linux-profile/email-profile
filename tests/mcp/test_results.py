"""Result shapes built from a parsed message."""

from __future__ import annotations

from email_profile.mcp.results import MessageDetail, MessageSummary, truncate
from email_profile.serializers.email import Message
from tests.conftest import SAMPLE_RFC822


def _message() -> Message:
    return Message.from_raw(uid="7", mailbox="INBOX", raw=SAMPLE_RFC822)


def test_truncate_short_text_untouched():
    assert truncate("abc", 10) == ("abc", False)
    assert truncate("abc", 0) == ("abc", False)


def test_truncate_appends_marker():
    body, cut = truncate("abcdef", 3)
    assert cut is True
    assert body == "abc\n…[truncated 3 chars]"


def test_summary_uses_from_alias():
    data = MessageSummary.of(_message()).model_dump(by_alias=True)
    assert data["from"] == "alice@example.com"
    assert data["uid"] == "7"
    assert data["date"].startswith("2030-01-01")


def test_detail_prefers_plain_text():
    detail = MessageDetail.of_message(_message(), 100)
    assert detail.body == "Hi Bob."
    assert detail.truncated is False
    assert detail.attachment_list == []
