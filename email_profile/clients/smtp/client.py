"""SMTP client for outgoing mail."""

from __future__ import annotations

import mimetypes
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Union

from email_profile.core.types import SMTPHost
from email_profile.retry import with_retry

AttachmentLike = Union[
    str,
    Path,
    tuple[str, bytes],
    tuple[str, bytes, str],
]


def _build_message(
    *,
    sender: str,
    to: Union[str, list[str]],
    subject: str,
    body: str = "",
    html: Optional[str] = None,
    cc: Optional[Union[str, list[str]]] = None,
    bcc: Optional[Union[str, list[str]]] = None,
    reply_to: Optional[str] = None,
    attachments: Optional[list[AttachmentLike]] = None,
    headers: Optional[dict[str, str]] = None,
) -> EmailMessage:
    """Build an :class:`email.message.EmailMessage` from keyword arguments."""

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to if isinstance(to, str) else ", ".join(to)
    msg["Subject"] = subject

    if cc:
        msg["Cc"] = cc if isinstance(cc, str) else ", ".join(cc)
    if bcc:
        msg["Bcc"] = bcc if isinstance(bcc, str) else ", ".join(bcc)
    if reply_to:
        msg["Reply-To"] = reply_to
    if headers:
        for name, value in headers.items():
            msg[name] = value

    msg.set_content(body or "")

    if html:
        msg.add_alternative(html, subtype="html")

    for item in attachments or []:
        _attach(msg, item)

    return msg


def _attach(msg: EmailMessage, item: AttachmentLike) -> None:
    if isinstance(item, (str, Path)):
        path = Path(item)
        data = path.read_bytes()
        filename = path.name
        ctype, _ = mimetypes.guess_type(filename)
    elif isinstance(item, tuple) and len(item) == 2:
        filename, data = item
        ctype, _ = mimetypes.guess_type(filename)
    elif isinstance(item, tuple) and len(item) == 3:
        filename, data, ctype = item
    else:
        raise TypeError(
            "Attachment must be a path, (name, bytes) or (name, bytes, mime)."
        )

    maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
    msg.add_attachment(
        data, maintype=maintype, subtype=subtype, filename=filename
    )


class SmtpClient:
    """Low-level SMTP client. Reuse via ``with`` for batch sends."""

    def __init__(
        self,
        *,
        host: SMTPHost,
        user: str,
        password: str,
    ) -> None:
        self._host = host
        self._user = user
        self._password = password
        self._smtp: Optional[smtplib.SMTP] = None

    @property
    def host(self) -> SMTPHost:
        return self._host

    @property
    def user(self) -> str:
        return self._user

    @property
    def is_connected(self) -> bool:
        return self._smtp is not None

    def connect(self) -> SmtpClient:
        if self._host.ssl:
            smtp: smtplib.SMTP = smtplib.SMTP_SSL(
                self._host.host, self._host.port
            )
        else:
            smtp = smtplib.SMTP(self._host.host, self._host.port)
            if self._host.starttls:
                smtp.starttls()
        smtp.login(self._user, self._password)
        self._smtp = smtp
        return self

    def close(self) -> None:
        if self._smtp is not None:
            try:
                self._smtp.quit()
            finally:
                self._smtp = None
                self._password = None

    def send(self, message: EmailMessage) -> None:
        """Send a pre-built message through the current SMTP session."""
        if self._smtp is None:
            raise RuntimeError(
                "SmtpClient is not connected. Use `with` or call connect()."
            )
        send_fn = with_retry()(self._smtp.send_message)
        send_fn(message)

    def __enter__(self) -> SmtpClient:
        return self.connect()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __repr__(self) -> str:
        state = "connected" if self.is_connected else "disconnected"
        return f"SmtpClient(host={self._host.host!r}, user={self._user!r}, {state})"
