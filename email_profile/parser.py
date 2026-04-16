"""RFC822 parser: headers, body parts, attachments."""

from __future__ import annotations

from datetime import datetime
from email import message_from_bytes
from email.header import decode_header
from email.message import Message as PyEmailMessage
from email.utils import parseaddr, parsedate_to_datetime
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict

_NAMED_HEADERS = frozenset(
    name.lower()
    for name in (
        "From",
        "To",
        "Cc",
        "Bcc",
        "Reply-To",
        "Message-ID",
        "In-Reply-To",
        "References",
        "Subject",
        "Date",
        "Content-Type",
        "List-Id",
        "List-Unsubscribe",
    )
)


class Attachment(BaseModel):
    """One attachment from an email."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    file_name: str
    content_type: str
    content: bytes

    def save(self, path: Union[str, Path] = ".") -> Path:
        """Write to path/<file_name>."""

        target = Path(path)
        target.mkdir(parents=True, exist_ok=True)

        out = target / self.file_name
        out.write_bytes(self.content)

        return out


class ParsedBody(BaseModel):
    """Decoded headers, body parts and attachments."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    message_id: Optional[str] = None
    date: Optional[datetime] = None
    from_: Optional[str] = None
    to_: Optional[str] = None

    subject: Optional[str] = None
    body_text_plain: str = ""
    body_text_html: str = ""
    content_type: Optional[str] = None

    cc: Optional[str] = None
    bcc: Optional[str] = None
    reply_to: Optional[str] = None

    in_reply_to: Optional[str] = None
    references: Optional[str] = None

    list_id: Optional[str] = None
    list_unsubscribe: Optional[str] = None

    attachments: list[Attachment] = []
    headers: dict[str, Union[str, list[str]]] = {}


def _decode_header(value: Optional[str]) -> str:
    if not value:
        return ""

    out = ""

    for chunk, encoding in decode_header(value):
        if isinstance(chunk, bytes):
            try:
                out += chunk.decode(encoding or "utf-8", errors="replace")
            except (LookupError, TypeError):
                out += chunk.decode("utf-8", errors="replace")
        else:
            out += chunk

    return out


def _decode_payload(part: PyEmailMessage) -> str:
    payload = part.get_payload(decode=True)

    if payload is None:
        return ""

    if isinstance(payload, bytes):
        charset = part.get_content_charset() or "utf-8"

        try:
            return payload.decode(charset, errors="replace")
        except (LookupError, TypeError):
            return payload.decode("utf-8", errors="replace")

    return str(payload)


def _coerce(value: object) -> Optional[str]:
    """Coerce a header value (str, Header, None) into str or None."""

    if value is None:
        return None

    if isinstance(value, str):
        return value

    return _decode_header(str(value))


def _h(message: PyEmailMessage, name: str) -> Optional[str]:
    """Get a header by name and coerce it to a plain string."""
    return _coerce(message.get(name))


def _extras(message: PyEmailMessage) -> dict[str, Union[str, list[str]]]:
    """Return non-named headers; repeats become lists."""

    bag: dict[str, Union[str, list[str]]] = {}

    for name, value in message.items():
        if name.lower() in _NAMED_HEADERS:
            continue

        coerced = _coerce(value)
        if coerced is None:
            continue

        if name in bag:
            existing = bag[name]
            if isinstance(existing, list):
                existing.append(coerced)
            else:
                bag[name] = [existing, coerced]
        else:
            bag[name] = coerced

    return bag


def parse_rfc822(raw_message: bytes) -> ParsedBody:
    """Parse RFC822 bytes into a ParsedBody."""

    message = message_from_bytes(raw_message)

    raw_date = message.get("Date")
    parsed_date = None
    if raw_date:
        try:
            parsed_date = parsedate_to_datetime(raw_date)
        except (TypeError, ValueError):
            parsed_date = None

    body = ParsedBody(
        message_id=_h(message, "Message-ID"),
        date=parsed_date,
        from_=parseaddr(message.get("From", ""))[1] or None,
        to_=parseaddr(message.get("To", ""))[1] or None,
        subject=_decode_header(message.get("Subject")),
        content_type=message.get_content_type(),
        cc=_h(message, "Cc"),
        bcc=_h(message, "Bcc"),
        reply_to=_h(message, "Reply-To"),
        in_reply_to=_h(message, "In-Reply-To"),
        references=_h(message, "References"),
        list_id=_h(message, "List-Id"),
        list_unsubscribe=_h(message, "List-Unsubscribe"),
        headers=_extras(message),
    )

    for part in message.walk():
        content_type = part.get_content_type()
        disposition = str(part.get("Content-Disposition") or "")

        if "attachment" in disposition.lower():
            filename = part.get_filename()
            if not filename:
                continue

            payload = part.get_payload(decode=True) or b""

            body.attachments.append(
                Attachment(
                    file_name=_decode_header(filename),
                    content_type=content_type,
                    content=(
                        payload
                        if isinstance(payload, bytes)
                        else str(payload).encode()
                    ),
                )
            )
            continue

        if content_type == "text/plain" and not body.body_text_plain:
            body.body_text_plain = _decode_payload(part)
        elif content_type == "text/html" and not body.body_text_html:
            body.body_text_html = _decode_payload(part)

    return body
