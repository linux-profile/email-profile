"""IMAP protocol parsers and email content parser."""

from __future__ import annotations

import re
from datetime import datetime
from email import message_from_bytes, message_from_string
from email.utils import parseaddr, parsedate_to_datetime
from hashlib import sha256
from typing import Optional

_UID_RE = re.compile(r"UID (\d+)")
_FLAGS_RE = re.compile(r"UID (\d+) FLAGS \(([^)]*)\)")
_FLAGS_ONLY_RE = re.compile(r"FLAGS \(([^)]*)\)")


class ImapFetch:
    """Decodes one IMAP fetch response entry."""

    __slots__ = ("_header", "_body")

    def __init__(self, entry: tuple) -> None:
        self._header = entry[0] if len(entry) > 0 else b""
        self._body = entry[1] if len(entry) > 1 else b""

    @staticmethod
    def is_valid(entry: object) -> bool:
        return isinstance(entry, tuple) and len(entry) >= 2

    def uid(self) -> Optional[str]:
        text = self._decode(self._header)
        match = _UID_RE.search(text)

        return match.group(1) if match else None

    def flags(self) -> Optional[str]:
        text = self._decode(self._header)
        match = _FLAGS_RE.search(text)
        return match.group(2) if match else None

    def flags_with_uid(self) -> Optional[tuple[str, str]]:
        text = self._decode(self._header)
        match = _FLAGS_RE.search(text)
        if match:
            return match.group(1), match.group(2)
        return None

    def message_id(self) -> Optional[str]:
        text = self._decode(self._body)
        for line in text.splitlines():
            if line.lower().startswith("message-id:"):
                value = line.split(":", 1)[1].strip()
                return value or None
        return None

    def message_id_or_hash(self) -> str:
        msg = message_from_bytes(self._body)
        message_id = msg.get("Message-ID")
        if message_id:
            return message_id
        return sha256(self._body).hexdigest()

    def raw(self) -> bytes:
        return self._body

    def text(self) -> str:
        return self._decode(self._body)

    def date(self) -> Optional[datetime]:
        msg = message_from_bytes(self._body)
        raw_date = msg.get("Date")
        if not raw_date:
            return None
        try:
            return parsedate_to_datetime(raw_date)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _decode(data: bytes, errors: str = "replace") -> str:
        if isinstance(data, bytes):
            return data.decode("utf-8", errors=errors)
        return str(data)

    @staticmethod
    def parse_flags(text: str) -> Optional[tuple[str, str]]:
        """Parse FLAGS from a raw bytes or text entry."""
        match = _FLAGS_RE.search(text)
        if match:
            return match.group(1), match.group(2)

        match = _FLAGS_ONLY_RE.search(text)
        if match:
            return "", match.group(1)

        return None

    @staticmethod
    def fetch_message_ids(
        client: object, uids: list[str], chunk_size: int = 500
    ) -> dict[str, str]:
        """Fetch Message-IDs from server. Returns {uid: message_id}."""

        result: dict[str, str] = {}

        for start in range(0, len(uids), chunk_size):
            group = uids[start : start + chunk_size]

            status, fetched = client.uid(
                "fetch",
                ",".join(group),
                "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])",
            )
            if status != "OK":
                continue

            for entry in fetched:
                if not ImapFetch.is_valid(entry):
                    continue

                d = ImapFetch(entry)
                uid = d.uid()
                msg_id = d.message_id()

                if uid and msg_id:
                    result[uid] = msg_id

        return result


class ImapSearch:
    """Decodes an IMAP SEARCH response."""

    __slots__ = ("_uids",)

    def __init__(self, data: list) -> None:
        if not data or not data[0]:
            self._uids: list[str] = []
        else:
            raw = data[0]
            text = (
                raw.decode("utf-8", errors="replace")
                if isinstance(raw, bytes)
                else str(raw)
            )
            self._uids = text.split()

    def uids(self) -> list[str]:
        return list(self._uids)

    def count(self) -> int:
        return len(self._uids)

    def is_empty(self) -> bool:
        return len(self._uids) == 0

    def __bool__(self) -> bool:
        return len(self._uids) > 0

    def __repr__(self) -> str:
        return f"ImapSearch({self.count()} uids)"


class EmailParser:
    """Parses RFC822 content (string or bytes)."""

    __slots__ = ("_msg",)

    def __init__(self, content: bytes | str) -> None:
        if isinstance(content, bytes):
            self._msg = message_from_bytes(content)
        else:
            self._msg = message_from_string(content)

    def message_id(self) -> Optional[str]:
        return self._msg.get("Message-ID")

    def message_id_or_hash(self, raw: bytes | str) -> str:
        mid = self.message_id()
        if mid:
            return mid
        data = raw if isinstance(raw, bytes) else raw.encode("utf-8")
        return sha256(data).hexdigest()

    def date(self) -> Optional[datetime]:
        raw_date = self._msg.get("Date")
        if not raw_date:
            return None
        try:
            return parsedate_to_datetime(raw_date)
        except (TypeError, ValueError):
            return None

    def subject(self) -> Optional[str]:
        return self._msg.get("Subject")

    def from_(self) -> Optional[str]:
        value = self._msg.get("From", "")
        return parseaddr(value)[1] or None

    def to(self) -> Optional[str]:
        value = self._msg.get("To", "")
        return parseaddr(value)[1] or None

    def header(self, name: str) -> Optional[str]:
        return self._msg.get(name)
