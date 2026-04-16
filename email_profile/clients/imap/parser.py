"""IMAP protocol parsers and email content parser."""

from __future__ import annotations

import re
from collections.abc import Iterator
from datetime import datetime
from email import message_from_bytes, message_from_string
from email.utils import parseaddr, parsedate_to_datetime
from hashlib import sha256
from typing import Optional

_UID_RE = re.compile(r"UID (\d+)")
_FLAGS_RE = re.compile(r"UID (\d+) FLAGS \(([^)]*)\)")
_FLAGS_ONLY_RE = re.compile(r"FLAGS \(([^)]*)\)")


class FetchParser:
    """Decodes one IMAP fetch response entry."""

    __slots__ = ("_header", "_body", "uid", "flags", "message_id")

    def __init__(self, entry: tuple) -> None:
        self._header = entry[0] if len(entry) > 0 else b""
        self._body = entry[1] if len(entry) > 1 else b""
        self.uid: str = ""
        self.flags: str = ""
        self.message_id: str = ""

    @staticmethod
    def is_valid(entry: object) -> bool:
        return isinstance(entry, tuple) and len(entry) >= 2

    def _parse_uid(self) -> Optional[str]:
        text = self._decode(self._header)
        match = _UID_RE.search(text)

        return match.group(1) if match else None

    def _parse_header_flags(self) -> Optional[str]:
        text = self._decode(self._header)
        match = _FLAGS_RE.search(text)
        return match.group(2) if match else None

    def _parse_header_flags_with_uid(self) -> Optional[tuple[str, str]]:
        text = self._decode(self._header)
        match = _FLAGS_RE.search(text)
        if match:
            return match.group(1), match.group(2)
        return None

    def _parse_message_id(self) -> Optional[str]:
        text = self._decode(self._body)

        for line in text.splitlines():
            if line.lower().startswith("message-id:"):
                value = line.split(":", 1)[1].strip()
                return value or None

        return None

    def _resolve_message_id(self) -> str:
        msg = message_from_bytes(self._body)
        mid = msg.get("Message-ID")

        if mid:
            return mid

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

    def _resolve_flags(self, trailing: object = None) -> str:
        """Return flags from the header, falling back to a trailing element."""
        flags = self._parse_header_flags() or ""

        if not flags and isinstance(trailing, bytes):
            parsed = self.parse_flags(self._decode(trailing))
            if parsed:
                flags = parsed[1]

        return flags

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
    def iter_entries(fetched: list) -> Iterator[FetchParser]:
        """Yield parsed entries with resolved flags."""
        offset = 0

        while offset < len(fetched):
            entry = fetched[offset]
            offset += 1

            if not FetchParser.is_valid(entry):
                continue

            parsed_entry = FetchParser(entry)
            uid = parsed_entry._parse_uid()
            if uid is None:
                continue

            trailing = fetched[offset] if offset < len(fetched) else None
            parsed_entry.uid = uid
            parsed_entry.flags = parsed_entry._resolve_flags(trailing)
            parsed_entry.message_id = parsed_entry._resolve_message_id()

            if trailing is not None and isinstance(trailing, bytes):
                offset += 1

            yield parsed_entry


class SearchParser:
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
        return f"SearchParser({self.count()} uids)"


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
