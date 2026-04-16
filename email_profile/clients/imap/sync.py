# ruff: noqa: ARG001
"""Sync (server->banco) and restore (banco->server) operations."""

from __future__ import annotations

import logging
import re
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from email import message_from_bytes, message_from_string
from email.utils import parsedate_to_datetime
from hashlib import sha256
from threading import Lock
from typing import TYPE_CHECKING, Callable, Optional

from rich.progress import Progress

from email_profile._internal import _state
from email_profile.clients.imap.client import ImapClient
from email_profile.clients.imap.mailbox import MailBox, _quote
from email_profile.core.abc import SyncResult
from email_profile.serializers.raw import RawSerializer

if TYPE_CHECKING:
    from email_profile.core.abc import StorageABC

logger = logging.getLogger(__name__)


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
        full: bool = False,
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
                except Exception:
                    if attempt < retries - 1:
                        time.sleep(2**attempt)
                        continue
                    with lock:
                        progress.console.print(
                            f"  [red]✗[/] {name} — connection failed ({retries} attempts)"
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

                    sync_fn = self.full_sync if full else self.sync
                    result = sync_fn(box, storage, on_progress=on_progress)

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
                except Exception:
                    if attempt < retries - 1:
                        time.sleep(2**attempt)
                        continue
                    if task is not None:
                        with lock:
                            progress.update(task, visible=False)
                    with lock:
                        progress.console.print(
                            f"  [red]✗[/] {name} — sync failed ({retries} attempts)"
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

        new_uids = self._filter_new_uids(
            mailbox,
            server_uids,
            existing_ids=storage.stored_ids(mailbox.name),
            existing_uids=storage.stored_uids(mailbox.name),
        )

        total = len(server_uids)
        result.skipped = total - len(new_uids)

        if on_progress is not None:
            on_progress(result.skipped, total)

        if not new_uids:
            return result

        uid_flags = self._fetch_flags(mailbox, new_uids)
        done = result.skipped

        for raw in self._fetch_raw(mailbox, new_uids, uid_flags):
            done += 1

            try:
                inserted = storage.save_raw(raw)
                if inserted:
                    result.inserted += 1
                else:
                    result.updated += 1
            except Exception as exc:
                logger.error("Failed to save %s: %s", raw.message_id, exc)
                result.errors.append(f"{raw.message_id}: {exc}")

            if on_progress is not None:
                on_progress(done, total)

        logger.info(
            "Synced %s: %d inserted, %d skipped, %d errors",
            result.mailbox,
            result.inserted,
            result.skipped,
            len(result.errors),
        )

        return result

    def full_sync(
        self,
        mailbox: MailBox,
        storage: StorageABC,
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> SyncResult:
        """Sync all emails from a mailbox, skipping nothing."""

        result = SyncResult(mailbox=mailbox.name)

        server_uids = mailbox.where().uids()
        total = len(server_uids)

        if on_progress is not None:
            on_progress(0, total)

        if not server_uids:
            return result

        uid_flags = self._fetch_flags(mailbox, server_uids)

        for done, raw in enumerate(
            self._fetch_raw(mailbox, server_uids, uid_flags), 1
        ):
            try:
                inserted = storage.save_raw(raw)
                if inserted:
                    result.inserted += 1
                else:
                    result.updated += 1
            except Exception as exc:
                logger.error("Failed to save %s: %s", raw.message_id, exc)
                result.errors.append(f"{raw.message_id}: {exc}")

            if on_progress is not None:
                on_progress(done, total)

        logger.info(
            "Full synced %s: %d inserted, %d updated, %d errors",
            result.mailbox,
            result.inserted,
            result.updated,
            len(result.errors),
        )

        return result

    @staticmethod
    def _fetch_raw(
        mailbox: MailBox,
        uids: list[str],
        uid_flags: dict[str, str],
    ) -> Iterator[RawSerializer]:
        """Fetch RFC822 content and yield RawSerializer without parsing."""

        client = mailbox._client
        if client is None:
            return

        _state(client.select(_quote(mailbox.name)))
        chunk_size = 100

        for start in range(0, len(uids), chunk_size):
            group = uids[start : start + chunk_size]

            status, fetched = client.uid("fetch", ",".join(group), "(RFC822)")
            if status != "OK":
                continue

            for entry in fetched:
                if not isinstance(entry, tuple):
                    continue

                header = entry[0].decode()
                uid_match = re.search(r"UID (\d+)", header)
                uid = uid_match.group(1) if uid_match else header.split()[0]

                raw_bytes = entry[1]
                file = raw_bytes.decode("utf-8", errors="replace")

                msg = message_from_bytes(raw_bytes)
                message_id = msg.get("Message-ID")
                if not message_id:
                    message_id = sha256(raw_bytes).hexdigest()

                yield RawSerializer(
                    message_id=message_id,
                    uid=uid,
                    mailbox=mailbox.name,
                    flags=uid_flags.get(uid, ""),
                    file=file,
                )

    @staticmethod
    def _fetch_flags(mailbox: MailBox, uids: list[str]) -> dict[str, str]:
        """Fetch FLAGS for a list of UIDs."""

        client = mailbox._client
        if client is None:
            return {}

        _state(client.select(_quote(mailbox.name)))
        result: dict[str, str] = {}
        chunk_size = 500

        for start in range(0, len(uids), chunk_size):
            group = uids[start : start + chunk_size]
            status, fetched = client.uid("fetch", ",".join(group), "(FLAGS)")
            if status != "OK":
                continue

            for entry in fetched:
                if not isinstance(entry, tuple):
                    if isinstance(entry, bytes):
                        text = entry.decode("utf-8", errors="replace")
                        match = re.search(r"UID (\d+) FLAGS \(([^)]*)\)", text)
                        if match:
                            result[match.group(1)] = match.group(2)
                    continue

                text = entry[0].decode("utf-8", errors="replace")
                match = re.search(r"UID (\d+) FLAGS \(([^)]*)\)", text)
                if match:
                    result[match.group(1)] = match.group(2)

        return result

    @staticmethod
    def _filter_new_uids(
        mailbox: MailBox,
        uids: list[str],
        existing_ids: set[str],
        existing_uids: set[str],
    ) -> list[str]:
        """Fetch only Message-IDs from server and return UIDs not in storage."""

        if not uids:
            return []

        client = mailbox._client
        if client is None:
            return uids

        _state(client.select(_quote(mailbox.name)))

        new_uids: list[str] = []
        chunk_size = 500

        for start in range(0, len(uids), chunk_size):
            group = uids[start : start + chunk_size]

            status, fetched = client.uid(
                "fetch",
                ",".join(group),
                "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])",
            )
            if status != "OK":
                new_uids.extend(group)
                continue

            for entry in fetched:
                if not isinstance(entry, tuple):
                    continue

                header = entry[0].decode()
                uid_match = re.search(r"UID (\d+)", header)
                raw_uid = (
                    uid_match.group(1) if uid_match else header.split()[0]
                )

                if raw_uid in existing_uids:
                    continue

                text = entry[1].decode("utf-8", errors="replace")
                msg_id = None

                for line in text.splitlines():
                    if line.lower().startswith("message-id:"):
                        msg_id = line.split(":", 1)[1].strip()
                        break

                if msg_id is not None and msg_id in existing_ids:
                    continue

                new_uids.append(raw_uid)

        return new_uids


class Restore:
    """Restore from local storage/files back to an IMAP server (storage -> server)."""

    def __init__(self, session: ImapClient) -> None:
        self._session = session

    def restore(
        self,
        storage: StorageABC,
        mailbox: Optional[str] = None,
        skip_duplicates: bool = True,
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

        count = 0
        progress = Progress()

        with progress:
            tasks: dict[str, object] = {}
            for box_name, raws in by_mailbox.items():
                tasks[box_name] = progress.add_task(
                    f"[cyan]{box_name}", total=len(raws)
                )

            server_ids_cache: dict[str, set[str]] = {}

            for box_name, raws in by_mailbox.items():
                if box_name not in self._session.mailboxes:
                    _state(self._session.client.create(_quote(box_name)))

                    details = _state(self._session.client.list())
                    for detail in details:
                        mailbox = MailBox.from_imap_detail(
                            client=self._session.client, detail=detail
                        )
                        if mailbox.name == box_name:
                            self._session.mailboxes[box_name] = mailbox
                            break

                    logger.info("Created mailbox %r on server", box_name)

                if skip_duplicates and box_name not in server_ids_cache:
                    server_ids_cache[box_name] = self._stored_ids(box_name)

                for raw in raws:
                    if skip_duplicates:
                        if raw.message_id in server_ids_cache[box_name]:
                            progress.advance(tasks[box_name])
                            continue
                        server_ids_cache[box_name].add(raw.message_id)

                    date = self._parse_date(raw.file)
                    self._session.mailboxes[box_name].append(
                        raw.file, flags=raw.flags, date=date
                    )
                    count += 1
                    progress.advance(tasks[box_name])

        return count

    @staticmethod
    def _parse_date(rfc822: str) -> Optional[datetime]:
        try:
            msg = message_from_string(rfc822)
            raw_date = msg.get("Date")
            if raw_date:
                return parsedate_to_datetime(raw_date)
        except (TypeError, ValueError):
            pass
        return None

    def _stored_ids(self, mailbox_name: str) -> set[str]:

        ids: set[str] = set()
        client = self._session.client
        if client is None:
            return ids

        _state(client.select(_quote(mailbox_name)))
        status, data = client.uid("search", None, "ALL")
        if status != "OK" or not data or not data[0]:
            return ids

        uids = data[0].decode().split()
        if not uids:
            return ids

        status, fetched = client.uid(
            "fetch",
            ",".join(uids),
            "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])",
        )
        if status != "OK":
            return ids

        for entry in fetched:
            if not isinstance(entry, tuple):
                continue
            _, raw = entry
            text = raw.decode("utf-8", errors="replace")
            for line in text.splitlines():
                if line.lower().startswith("message-id:"):
                    ids.add(line.split(":", 1)[1].strip())
                    break
        return ids
