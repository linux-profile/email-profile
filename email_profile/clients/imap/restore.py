# ruff: noqa: ARG001
"""Restore from local storage back to an IMAP server (storage -> server)."""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import TYPE_CHECKING, Optional

from rich.progress import Progress

from email_profile.clients.imap.client import ImapClient
from email_profile.clients.imap.fetch import Fetch
from email_profile.clients.imap.mailbox import MailBox, _quote
from email_profile.clients.imap.parser import (
    EmailParser,
    SearchParser,
)
from email_profile.core.status import Status

if TYPE_CHECKING:
    from email_profile.core.abc import StorageABC

logger = logging.getLogger(__name__)


class Restore:
    """Restore from local storage/files back to an IMAP server (storage -> server)."""

    def __init__(self, session: ImapClient) -> None:
        self._session = session

    def orchestrate(
        self,
        storage: StorageABC,
        mailbox: Optional[str] = None,
        skip_duplicates: bool = True,
        max_workers: int = 3,
    ) -> int:
        """Restore all mailboxes with progress and parallel upload."""
        self._session.require()

        ids_by_mailbox: dict[str, list[str]] = {}

        for message_id in storage.ids():
            raw = storage.get(message_id)
            if raw is None or not raw.file:
                continue
            if mailbox and raw.mailbox != mailbox:
                continue
            ids_by_mailbox.setdefault(raw.mailbox, []).append(message_id)
            del raw

        if not ids_by_mailbox:
            return 0

        total_count = 0
        lock = Lock()
        progress = Progress()

        def restore_one(
            box_name: str, message_ids: list[str], retries: int = 3
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
                except Exception as exc:
                    if attempt < retries - 1:
                        time.sleep(2**attempt)
                        continue
                    with lock:
                        progress.console.print(
                            f"  [red]✗[/] {box_name} — connection failed: {exc}"
                        )
                    return 0

                try:
                    _ensure_mailbox(session, box_name)

                    with lock:
                        task = progress.add_task(
                            f"  [cyan]{box_name}", total=len(message_ids)
                        )

                    result = self.restore_mailbox(
                        session,
                        box_name,
                        message_ids,
                        storage=storage,
                        skip_duplicates=skip_duplicates,
                    )

                    with lock:
                        progress.update(task, visible=False)
                        progress.console.print(
                            f"  [green]✓[/] {box_name} — "
                            f"{result['uploaded']} uploaded, "
                            f"{result['skipped']} skipped"
                        )

                    return result["uploaded"]
                except Exception as exc:
                    if attempt < retries - 1:
                        time.sleep(2**attempt)
                        continue
                    if task is not None:
                        with lock:
                            progress.update(task, visible=False)
                    with lock:
                        progress.console.print(
                            f"  [red]✗[/] {box_name} — restore failed: {exc}"
                        )
                    return 0
                finally:
                    session.close()

            return 0

        with (
            progress,
            ThreadPoolExecutor(
                max_workers=min(max_workers, len(ids_by_mailbox))
            ) as pool,
        ):
            futures = {
                pool.submit(restore_one, box_name, msg_ids): box_name
                for box_name, msg_ids in ids_by_mailbox.items()
            }
            for future in as_completed(futures):
                total_count += future.result()

        return total_count

    @staticmethod
    def restore_mailbox(
        session: ImapClient,
        box_name: str,
        message_ids: list[str],
        *,
        storage: StorageABC,
        skip_duplicates: bool = True,
    ) -> dict[str, int]:
        """Restore a single mailbox. Returns {'uploaded': N, 'skipped': N}.

        Messages are loaded from *storage* one at a time so that only
        one RFC-822 body is kept in memory per iteration, avoiding OOM
        on large backups.
        """

        server_ids: set[str] = set()
        if skip_duplicates:
            server_ids = _server_message_ids(session.client, box_name)

        uploaded = 0
        skipped = 0

        for mid in message_ids:
            if skip_duplicates and mid in server_ids:
                skipped += 1
                continue

            raw = storage.get(mid)
            if raw is None or not raw.file:
                continue

            server_ids.add(mid)

            date = EmailParser(raw.file).date()
            session.mailboxes[box_name].append(
                raw.file, flags=raw.flags, date=date
            )
            uploaded += 1
            del raw

        return {"uploaded": uploaded, "skipped": skipped}


def _ensure_mailbox(session: ImapClient, box_name: str) -> None:
    if box_name in session.mailboxes:
        return

    Status.state(session.client.create(_quote(box_name)))

    details = Status.state(session.client.list())
    for detail in details:
        mailbox = MailBox.from_imap_detail(
            client=session.client, detail=detail
        )
        if mailbox.name == box_name:
            session.mailboxes[box_name] = mailbox
            break

    logger.info("Created mailbox %r on server", box_name)


def _server_message_ids(client: object, mailbox_name: str) -> set[str]:
    ids: set[str] = set()

    Status.state(client.select(_quote(mailbox_name)))
    status, data = client.uid("search", None, "ALL")
    if status != "OK" or not data or not data[0]:
        return ids

    search = SearchParser(data)
    if search.is_empty():
        return ids

    msg_ids = Fetch.fetch_message_ids(client, search.uids())
    ids.update(msg_ids.values())

    return ids
