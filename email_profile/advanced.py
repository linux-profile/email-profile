"""Advanced / power-user symbols.

Anything that is not part of the "read inbox in 4 lines" experience lives
here. The top-level ``email_profile`` module only exposes the essentials;
everything else is available from this submodule::

    from email_profile.advanced import resolve_imap_host, Where, MailBox
"""

from __future__ import annotations

from email_profile.dump import MessageDumper
from email_profile.eml import EmailModel
from email_profile.errors import Retryable
from email_profile.mailbox import AppendedUID, MailBox
from email_profile.parser import Attachment, ParsedBody, parse_rfc822
from email_profile.protocols import StorageProtocol
from email_profile.providers import (
    IMAPHost,
    ProviderResolutionError,
    resolve_imap_host,
    resolve_smtp_host,
)
from email_profile.retry import with_retry
from email_profile.searches import Where
from email_profile.smtp import SmtpClient
from email_profile.status import IMAPError, Status
from email_profile.types import SMTPHost

__all__ = [
    "AppendedUID",
    "Attachment",
    "EmailModel",
    "IMAPError",
    "IMAPHost",
    "MailBox",
    "MessageDumper",
    "ParsedBody",
    "ProviderResolutionError",
    "Retryable",
    "SMTPHost",
    "SmtpClient",
    "Status",
    "StorageProtocol",
    "Where",
    "parse_rfc822",
    "resolve_imap_host",
    "resolve_smtp_host",
    "with_retry",
]
