"""High-level send / reply / forward on top of SmtpClient."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Optional, Union

from email_profile.clients.imap.client import ImapClient
from email_profile.clients.smtp.client import (
    AttachmentLike,
    SmtpClient,
    _build_message,
)
from email_profile.providers import resolve_smtp_host

if TYPE_CHECKING:
    from email.message import EmailMessage

    from email_profile.clients.imap.folders import FolderAccess
    from email_profile.core.types import SMTPHost
    from email_profile.serializers.email import EmailSerializer


class Sender:
    """Outgoing-mail facade: send, reply, forward."""

    def __init__(self, session: ImapClient, folders: FolderAccess) -> None:
        self._session = session
        self._folders = folders
        self._smtp_host: Optional[SMTPHost] = None

    def smtp_host(self) -> SMTPHost:
        """Resolved SMTP host for this account. Cached after first call."""
        if self._smtp_host is None:
            self._smtp_host = resolve_smtp_host(self._session.user)
        return self._smtp_host

    def send(
        self,
        to: Union[str, list[str]],
        subject: str,
        body: str = "",
        *,
        html: Optional[str] = None,
        cc: Optional[Union[str, list[str]]] = None,
        bcc: Optional[Union[str, list[str]]] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[list[AttachmentLike]] = None,
        headers: Optional[dict[str, str]] = None,
        save_to_sent: bool = True,
    ) -> None:
        """Send an email via SMTP, optionally appending to Sent."""
        message = _build_message(
            sender=self._session.user,
            to=to,
            subject=subject,
            body=body,
            html=html,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
            attachments=attachments,
            headers=headers,
        )
        self.send_message(message, save_to_sent=save_to_sent)

    def send_message(
        self,
        message: EmailMessage,
        *,
        save_to_sent: bool = True,
    ) -> None:
        """Send a pre-built EmailMessage."""
        if not message.get("From"):
            message["From"] = self._session.user

        with SmtpClient(
            host=self.smtp_host(),
            user=self._session.user,
            password=self._session.password,
        ) as client:
            client.send(message)

        if save_to_sent and self._session.is_connected:
            with contextlib.suppress(KeyError):
                self._folders.sent.append(message.as_bytes())

    def reply(
        self,
        original: EmailSerializer,
        body: str = "",
        *,
        html: Optional[str] = None,
        attachments: Optional[list[AttachmentLike]] = None,
        reply_all: bool = False,
        save_to_sent: bool = True,
    ) -> None:
        """Reply to a previously-fetched message, preserving threading."""
        subject = original.subject or ""
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"

        to = original.reply_to or original.from_ or ""
        cc = original.cc if reply_all else None

        headers: dict[str, str] = {}
        if original.id:
            headers["In-Reply-To"] = original.id
            refs = (original.references or "").split()
            refs.append(original.id)
            headers["References"] = " ".join(refs)

        self.send(
            to=to,
            subject=subject,
            body=body,
            html=html,
            cc=cc,
            attachments=attachments,
            headers=headers,
            save_to_sent=save_to_sent,
        )

    def forward(
        self,
        original: EmailSerializer,
        to: Union[str, list[str]],
        body: str = "",
        *,
        attachments: Optional[list[AttachmentLike]] = None,
        save_to_sent: bool = True,
    ) -> None:
        """Forward a previously-fetched message to new recipients."""
        subject = original.subject or ""
        if not subject.lower().startswith("fwd:"):
            subject = f"Fwd: {subject}"

        quoted = (
            f"\n\n---------- Forwarded message ----------\n"
            f"From: {original.from_}\n"
            f"Date: {original.date}\n"
            f"Subject: {original.subject}\n"
            f"To: {original.to_}\n\n"
            f"{original.body_text_plain}"
        )

        self.send(
            to=to,
            subject=subject,
            body=(body + quoted) if body else quoted,
            attachments=attachments,
            save_to_sent=save_to_sent,
        )
