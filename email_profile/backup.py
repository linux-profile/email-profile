"""Restore operations: re-upload a backup to the server."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from email_profile.imap_session import IMAPSession

if TYPE_CHECKING:
    from email_profile.protocols import StorageProtocol


class RestoreOps:
    """Idempotent restore of persisted messages back to an IMAP server."""

    def __init__(self, session: IMAPSession) -> None:
        self._session = session

    def restore(
        self,
        storage: StorageProtocol,
        mailbox: Optional[str] = None,
        target: Optional[str] = None,
        skip_duplicates: bool = True,
    ) -> int:
        """Re-upload every message persisted in storage to this server."""
        self._session.require()
        count = 0
        seen_ids: dict[str, set[str]] = {}

        for serializer in storage.messages(mailbox=mailbox):
            box_name = target or serializer.mailbox
            if box_name not in self._session.mailboxes:
                raise KeyError(
                    f"Target mailbox {box_name!r} does not exist. "
                    f"Available: {list(self._session.mailboxes)}"
                )

            if skip_duplicates:
                if box_name not in seen_ids:
                    seen_ids[box_name] = self._existing_ids(box_name)
                if serializer.id and serializer.id in seen_ids[box_name]:
                    continue
                if serializer.id:
                    seen_ids[box_name].add(serializer.id)

            self._session.mailboxes[box_name].append(serializer)
            count += 1

        return count

    def restore_eml(
        self,
        path: Union[str, Path],
        target: Optional[str] = None,
    ) -> int:
        """Re-upload every .eml under path; mailbox = parent dir name."""
        self._session.require()
        source = Path(path)
        if not source.exists():
            raise FileNotFoundError(source)

        count = 0
        for eml_path in source.rglob("*.eml"):
            box_name = target or eml_path.parent.name
            if box_name not in self._session.mailboxes:
                raise KeyError(
                    f"Target mailbox {box_name!r} does not exist. "
                    f"Available: {list(self._session.mailboxes)}"
                )
            self._session.mailboxes[box_name].append(eml_path.read_bytes())
            count += 1

        return count

    def _existing_ids(self, mailbox_name: str) -> set[str]:
        """Collect Message-IDs already present in a server mailbox."""
        from email_profile._internal import _state

        ids: set[str] = set()
        client = self._session.client
        if client is None:
            return ids

        _state(client.select(mailbox_name))
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
