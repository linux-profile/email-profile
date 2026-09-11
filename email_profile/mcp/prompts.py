"""Prompts that put the tools in the order an email task actually needs.

The costly mistakes live in the order: replying before reading the whole
thread, sending before the user saw the text, deleting before confirming
which message.
"""

from __future__ import annotations

from typing import Any


def register(mcp: Any) -> None:
    @mcp.prompt(
        title="Triage inbox",
        description="Summarize what is new and what needs an answer.",
    )
    def triage_inbox(mailbox: str = "INBOX", limit: str = "20") -> str:
        return (
            f"Call search_messages with mailbox={mailbox}, unseen=true and "
            f"limit={limit}. Group the rows by sender and say, for each, "
            "what it is about and whether it seems to need a reply.\n\n"
            "Read a message with read_message only when the subject is "
            "not enough to decide. Do not mark anything as seen, and do "
            "not reply — just report."
        )

    @mcp.prompt(
        title="Find a message",
        description="Locate one message from a description.",
    )
    def find_message(query: str = "", mailbox: str = "INBOX") -> str:
        return (
            "Find the message the user describes.\n\n"
            f"Description: {query or 'ask the user'}. Mailbox: {mailbox}.\n\n"
            "Start with search_messages using the most specific filter "
            "available — `sender` when a person is named, `subject` when "
            "words from the title are given, `text` otherwise. Narrow "
            "with `since`/`before` when a period is mentioned.\n\n"
            "When several rows match, list them with date, sender and "
            "subject and let the user pick. Keep the uid and mailbox of "
            "the chosen one for follow-up tools."
        )

    @mcp.prompt(
        title="Draft a reply",
        description="Write a reply and get it approved before sending.",
    )
    def draft_reply(mailbox: str = "INBOX", uid: str = "") -> str:
        return (
            "Draft a reply to a message.\n\n"
            + (
                f"Mailbox: {mailbox}, uid: {uid}.\n\n"
                if uid
                else "Find the message with search_messages first.\n\n"
            )
            + "Call read_message and read the whole body — set max_chars "
            "higher if it came back truncated. Write the reply in the "
            "same language and tone as the original.\n\n"
            "Show the user the full text and ask for approval. Only then "
            "call reply_message; if that tool is not available the "
            "server was started without --allow-send, so hand the text "
            "to the user instead."
        )

    @mcp.prompt(
        title="Summarize a thread",
        description="Condense a conversation into decisions and open points.",
    )
    def summarize_thread(subject: str = "", mailbox: str = "INBOX") -> str:
        return (
            "Summarize an email thread.\n\n"
            f"Subject: {subject or 'ask the user'}. Mailbox: {mailbox}.\n\n"
            "Call search_messages with subject set to the thread's title "
            "and read each row oldest to newest with read_message. Report "
            "who said what, in order, then list decisions taken and "
            "questions still open. Quote dates as they appear."
        )
