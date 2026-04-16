# ruff: noqa: ARG001
"""Sync server state into local storage (server -> storage)."""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import TYPE_CHECKING, Callable, Optional

from rich.progress import Progress

from email_profile._internal import _state
from email_profile.clients.imap.client import ImapClient
from email_profile.clients.imap.fetch import F
from email_profile.clients.imap.mailbox import MailBox, _quote
from email_profile.clients.imap.protocol import ImapFetch
from email_profile.core.abc import SyncResult
from email_profile.serializers.raw import RawSerializer

if TYPE_CHECKING:
    from email_profile.core.abc import StorageABC

logger = logging.getLogger(__name__)

CHUNK_FETCH = 100
CHUNK_HEADER = 500


class Sync:
    """Sync server state into local storage (server -> storage)."""

    def __init__(self, session: ImapClient) -> None:
        self._session = session

    def orchestrate(
        self,
        storage: StorageABC,
        mailbox: Optional[str] = None,
        mailbox_names: Optional[list[str]] = None,
        max_workers: int = 3,
    ) -> SyncResult:
        """Sync one or all mailboxes with progress and parallel fetch."""

        names = (
            [mailbox]
            if mailbox
            else mailbox_names or list(self._session.mailboxes)
        )
        combined = SyncResult(mailbox=mailbox or "*")
        lock = Lock()
        progress = Progress()

        def sync_one(name: str, retries: int = 3) -> SyncResult:
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
                            f"  [red]✗[/] {name} — connection failed: {exc}"
                        )
                    return SyncResult(mailbox=name)

                try:
                    box = session.mailboxes[name]
                    server_count = box.where().count()

                    with lock:
                        task = progress.add_task(
                            f"  [cyan]{name}",
                            total=max(server_count, 1),
                            completed=1 if server_count == 0 else 0,
                        )

                    def on_progress(done: int, total: int, _task=task) -> None:
                        with lock:
                            progress.update(_task, completed=done, total=total)

                    result = self.sync(box, storage, on_progress=on_progress)

                    with lock:
                        progress.update(task, visible=False)
                        msg = (
                            f"  [green]✓[/] {name} — "
                            f"{result.inserted} new, "
                            f"{result.updated} updated, "
                            f"{result.skipped} skipped"
                        )
                        if result.has_errors:
                            msg += f", [red]{len(result.errors)} errors[/]"
                        progress.console.print(msg)

                    return result
                except Exception as exc:
                    if attempt < retries - 1:
                        time.sleep(2**attempt)
                        continue
                    if task is not None:
                        with lock:
                            progress.update(task, visible=False)
                    with lock:
                        progress.console.print(
                            f"  [red]✗[/] {name} — sync failed: {exc}"
                        )
                    return SyncResult(mailbox=name)
                finally:
                    session.close()

            return SyncResult(mailbox=name)

        with (
            progress,
            ThreadPoolExecutor(
                max_workers=min(max_workers, len(names))
            ) as pool,
        ):
            futures = {pool.submit(sync_one, name): name for name in names}
            for future in as_completed(futures):
                combined = combined.merge(future.result())

        return combined

    def sync(
        self,
        mailbox: MailBox,
        storage: StorageABC,
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> SyncResult:
        """Sync one mailbox from IMAP into local storage."""

        result = SyncResult(mailbox=mailbox.name)
        server_uids = mailbox.where().uids()

        existing_uids = storage.uids(mailbox.name)
        new_uids = [u for u in server_uids if u not in existing_uids]

        total = len(server_uids)
        result.skipped = total - len(new_uids)

        if on_progress is not None:
            on_progress(result.skipped, total)

        if not new_uids:
            return result

        done = result.skipped

        for raw in _fetch_raw(mailbox, new_uids):
            done += 1
            _save_one(storage, raw, result)

            if on_progress is not None:
                on_progress(done, total)

        return result


def _save_one(
    storage: StorageABC, raw: RawSerializer, result: SyncResult
) -> None:
    try:
        inserted = storage.save(raw)
        if inserted:
            result.inserted += 1
        else:
            result.updated += 1
    except Exception as exc:
        logger.error("Failed to save %s: %s", raw.message_id, exc)
        result.errors.append(f"{raw.message_id}: {exc}")


def _fetch_raw(mailbox: MailBox, uids: list[str]) -> Iterator[RawSerializer]:
    """Fetch RFC822 + FLAGS and yield RawSerializer."""

    client = mailbox._client
    if client is None:
        return

    _state(client.select(_quote(mailbox.name)))
    spec = (F.rfc822() + F.flags()).mount()

    for start in range(0, len(uids), CHUNK_FETCH):
        group = uids[start : start + CHUNK_FETCH]

        status, fetched = client.uid("fetch", ",".join(group), spec)
        if status != "OK":
            continue

        i = 0

        while i < len(fetched):
            entry = fetched[i]
            i += 1

            if not ImapFetch.is_valid(entry):
                continue

            d = ImapFetch(entry)
            uid = d.uid()
            if uid is None:
                continue

            flags = d.flags() or ""

            if (
                not flags
                and i < len(fetched)
                and isinstance(fetched[i], bytes)
            ):
                text = ImapFetch._decode(fetched[i])
                parsed = ImapFetch.parse_flags(text)
                if parsed:
                    flags = parsed[1]
                i += 1

            yield RawSerializer(
                message_id=d.message_id_or_hash(),
                uid=uid,
                mailbox=mailbox.name,
                flags=flags,
                file=d.text(),
            )
