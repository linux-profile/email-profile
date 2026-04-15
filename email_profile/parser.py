"""RFC822 parser: headers, body parts, attachments."""

from __future__ import annotations

from email import message_from_bytes
from email.header import decode_header
from email.message import Message as PyEmailMessage
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
        "Sender",
        "Reply-To",
        "Message-ID",
        "In-Reply-To",
        "References",
        "Subject",
        "Date",
        "MIME-Version",
        "Content-Type",
        "Content-Transfer-Encoding",
        "Return-Path",
        "Delivered-To",
        "Received",
        "DKIM-Signature",
        "Authentication-Results",
        "ARC-Authentication-Results",
        "ARC-Message-Signature",
        "ARC-Seal",
        "List-Id",
        "List-Unsubscribe",
        "List-Unsubscribe-Post",
        "List-Post",
        "List-Help",
        "List-Archive",
        "List-Owner",
        "Importance",
        "Priority",
        "X-Priority",
        "Sensitivity",
        "Auto-Submitted",
        "Precedence",
        "X-SG-EID",
        "X-SG-ID",
        "X-Entity-ID",
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

    subject: Optional[str] = None
    body_text_plain: str = ""
    body_text_html: str = ""
    content_type: Optional[str] = None
    attachments: list[Attachment] = []

    cc: Optional[str] = None
    bcc: Optional[str] = None
    sender: Optional[str] = None
    reply_to: Optional[str] = None

    in_reply_to: Optional[str] = None
    references: Optional[str] = None

    mime_version: Optional[str] = None
    content_transfer_encoding: Optional[str] = None

    return_path: Optional[str] = None
    delivered_to: Optional[str] = None
    received: Optional[str] = None

    dkim_signature: Optional[str] = None
    authentication_results: Optional[str] = None
    arc_authentication_results: Optional[str] = None
    arc_message_signature: Optional[str] = None
    arc_seal: Optional[str] = None

    list_id: Optional[str] = None
    list_unsubscribe: Optional[str] = None
    list_unsubscribe_post: Optional[str] = None
    list_post: Optional[str] = None
    list_help: Optional[str] = None
    list_archive: Optional[str] = None
    list_owner: Optional[str] = None

    importance: Optional[str] = None
    priority: Optional[str] = None
    x_priority: Optional[str] = None
    sensitivity: Optional[str] = None
    auto_submitted: Optional[str] = None
    precedence: Optional[str] = None

    x_sg_eid: Optional[str] = None
    x_sg_id: Optional[str] = None
    x_entity_id: Optional[str] = None

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

    body = ParsedBody(
        subject=_decode_header(message.get("Subject")),
        content_type=message.get_content_type(),
        cc=_h(message, "Cc"),
        bcc=_h(message, "Bcc"),
        sender=_h(message, "Sender"),
        reply_to=_h(message, "Reply-To"),
        in_reply_to=_h(message, "In-Reply-To"),
        references=_h(message, "References"),
        mime_version=_h(message, "MIME-Version"),
        content_transfer_encoding=_h(message, "Content-Transfer-Encoding"),
        return_path=_h(message, "Return-Path"),
        delivered_to=_h(message, "Delivered-To"),
        received=_h(message, "Received"),
        dkim_signature=_h(message, "DKIM-Signature"),
        authentication_results=_h(message, "Authentication-Results"),
        arc_authentication_results=_h(message, "ARC-Authentication-Results"),
        arc_message_signature=_h(message, "ARC-Message-Signature"),
        arc_seal=_h(message, "ARC-Seal"),
        list_id=_h(message, "List-Id"),
        list_unsubscribe=_h(message, "List-Unsubscribe"),
        list_unsubscribe_post=_h(message, "List-Unsubscribe-Post"),
        list_post=_h(message, "List-Post"),
        list_help=_h(message, "List-Help"),
        list_archive=_h(message, "List-Archive"),
        list_owner=_h(message, "List-Owner"),
        importance=_h(message, "Importance"),
        priority=_h(message, "Priority"),
        x_priority=_h(message, "X-Priority"),
        sensitivity=_h(message, "Sensitivity"),
        auto_submitted=_h(message, "Auto-Submitted"),
        precedence=_h(message, "Precedence"),
        x_sg_eid=_h(message, "X-SG-EID"),
        x_sg_id=_h(message, "X-SG-ID"),
        x_entity_id=_h(message, "X-Entity-ID"),
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
