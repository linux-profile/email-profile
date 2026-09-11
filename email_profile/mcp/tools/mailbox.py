"""Mailbox tools: list folders and search inside one."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Any, Optional

from pydantic import Field

from email_profile.clients.imap.query import Q
from email_profile.mcp.annotations import READ_ONLY
from email_profile.mcp.config import MAX_LIMIT, Settings
from email_profile.mcp.params import Mailbox
from email_profile.mcp.results import MessageSummary, SearchPage
from email_profile.mcp.session import Session


def register(mcp: Any, session: Session, settings: Settings) -> None:
    @mcp.tool(annotations=READ_ONLY)
    def list_mailboxes() -> list[str]:
        """List every mailbox (folder) on the server, by server-side name.

        Use the exact names returned here as `mailbox` in other tools —
        Gmail, for instance, calls Sent `[Gmail]/Sent Mail`.
        """
        with session.lock:
            return session.email.mailboxes()

    @mcp.tool(annotations=READ_ONLY)
    def search_messages(
        mailbox: Mailbox = settings.default_mailbox,
        text: Optional[str] = None,
        subject: Optional[str] = None,
        sender: Annotated[
            Optional[str], Field(description="Match on the From header.")
        ] = None,
        to: Optional[str] = None,
        unseen: Optional[bool] = None,
        flagged: Optional[bool] = None,
        since: Optional[date] = None,
        before: Optional[date] = None,
        limit: Annotated[int, Field(ge=1, le=MAX_LIMIT)] = settings.limit,
        offset: Annotated[int, Field(ge=0)] = 0,
    ) -> SearchPage:
        """Search one mailbox. Returns headers only, newest first.

        Every filter is optional and they combine with AND; no filter
        returns everything. `text` searches headers and body, `subject`
        and `sender` match their header. Dates are inclusive of `since`
        and exclusive of `before`.

        Read a message with `read_message` using the `uid` and `mailbox`
        of a row. Page with `offset` = `next_offset` until it is null.
        """
        kwargs: dict[str, Any] = {}
        if text:
            kwargs["text"] = text
        if subject:
            kwargs["subject"] = subject
        if sender:
            kwargs["from_who"] = sender
        if to:
            kwargs["to"] = to
        if unseen is not None:
            kwargs["unseen"] = unseen
        if flagged is not None:
            kwargs["flagged"] = flagged
        if since:
            kwargs["since"] = since
        if before:
            kwargs["before"] = before

        with session.lock:
            folder = session.email.mailbox(mailbox)
            uids = list(reversed(folder.where(**kwargs).uids()))
            page = uids[offset : offset + limit]

            rows: list[MessageSummary] = []
            if page:
                fetched = folder.where(Q.uid_set(page)).messages(
                    mode="headers"
                )
                rows = [MessageSummary.of(m) for m in fetched]
                order = {uid: i for i, uid in enumerate(page)}
                rows.sort(key=lambda r: order.get(r.uid, len(page)))

        end = offset + len(page)
        return SearchPage(
            mailbox=mailbox,
            total=len(uids),
            offset=offset,
            limit=limit,
            next_offset=end if end < len(uids) else None,
            messages=rows,
        )
