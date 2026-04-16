# ruff: noqa: ARG001
"""Restore from local storage back to an IMAP server (storage -> server)."""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import TYPE_CHECKING, Optional

from rich.progress import Progress

from email_profile._internal import _state
from email_profile.clients.imap.client import ImapClient
from email_profile.clients.imap.mailbox import MailBox, _quote
from email_profile.clients.imap.protocol import (
    EmailParser,
    ImapFetch,
    ImapSearch,
)
from email_profile.serializers.raw import RawSerializer

if TYPE_CHECKING:
    from email_profile.core.abc import StorageABC

logger = logging.getLogger(__name__)


class Restore:
    """Restore from local storage/files back to an IMAP server (storage -> server)."""

    def __init__(self, session: ImapClient) -> None:
        self._session = session

    def restore(
        self,
        storage: StorageABC,
        mailbox: Optional[str] = None,
        skip_duplicates: bool = True,
        max_workers: int = 3,
    ) -> int:
        """Re-upload every message persisted in storage to this server."""
        self._session.require()

        by_mailbox: dict[str, list[RawSerializer]] = {}

        for message_id in storage.stored_ids():
            raw = storage.get_raw(message_id)
            if raw is None or not raw.file:
                continue
            if mailbox and raw.mailbox != mailbox:
                continue
            by_mailbox.setdefault(raw.mailbox, []).append(raw)

        if not by_mailbox:
            return 0

        total_count = 0
        lock = Lock()
        progress = Progress()

        def restore_one(
            box_name: str, raws: list[RawSerializer], retries: int = 3
        ) -> int:
            task = None

            for attempt in range(retries):
                session = ImapClient(
                    server=self._session.server,
                    user=self._session.user,
                    password=self._session.password,
                    port=self._session.port,
                    ssl=self._session.ssl,
                )

                try:
                    session.connect()
                except Exception:
                    if attempt < retries - 1:
                        time.sleep(2**attempt)
                        continue
                    with lock:
                        progress.console.print(
                            f"  [red]✗[/] {box_name} — connection failed ({retries} attempts)"
                        )
                    return 0

                try:
                    if box_name not in session.mailboxes:
                        _state(session.client.create(_quote(box_name)))
                        details = _state(session.client.list())
                        for detail in details:
                            mb = MailBox.from_imap_detail(
                                client=session.client, detail=detail
                            )
                            if mb.name == box_name:
                                session.mailboxes[box_name] = mb
                                break

                    with lock:
                        task = progress.add_task(
                            f"  [cyan]{box_name}", total=len(raws)
                        )

                    server_ids: set[str] = set()
                    if skip_duplicates:
                        server_ids = _server_message_ids(
                            session.client, box_name
                        )

                    uploaded = 0
                    skipped = 0

                    for raw in raws:
                        if skip_duplicates:
                            if raw.message_id in server_ids:
                                skipped += 1
                                with lock:
                                    progress.advance(task)
                                continue
                            server_ids.add(raw.message_id)

                        date = EmailParser(raw.file).date()
                        session.mailboxes[box_name].append(
                            raw.file, flags=raw.flags, date=date
                        )
                        uploaded += 1
                        with lock:
                            progress.advance(task)

                    with lock:
                        progress.update(task, visible=False)
                        progress.console.print(
                            f"  [green]✓[/] {box_name} — "
                            f"{uploaded} uploaded, "
                            f"{skipped} skipped"
                        )

                    return uploaded
                except Exception:
                    if attempt < retries - 1:
                        time.sleep(2**attempt)
                        continue
                    if task is not None:
                        with lock:
                            progress.update(task, visible=False)
                    with lock:
                        progress.console.print(
                            f"  [red]✗[/] {box_name} — restore failed ({retries} attempts)"
                        )
                    return 0
                finally:
                    session.close()

            return 0

        with (
            progress,
            ThreadPoolExecutor(
                max_workers=min(max_workers, len(by_mailbox))
            ) as pool,
        ):
            futures = {
                pool.submit(restore_one, box_name, raws): box_name
                for box_name, raws in by_mailbox.items()
            }
            for future in as_completed(futures):
                total_count += future.result()

        return total_count


def _server_message_ids(client: object, mailbox_name: str) -> set[str]:
    ids: set[str] = set()

    _state(client.select(_quote(mailbox_name)))
    status, data = client.uid("search", None, "ALL")
    if status != "OK" or not data or not data[0]:
        return ids

    search = ImapSearch(data)
    if search.is_empty():
        return ids

    msg_ids = ImapFetch.fetch_message_ids(client, search.uids())
    ids.update(msg_ids.values())

    return ids
