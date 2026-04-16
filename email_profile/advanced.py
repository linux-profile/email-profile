"""Advanced / power-user symbols."""

from __future__ import annotations

from email_profile.clients.imap_client import ImapClient
from email_profile.clients.smtp_client import SmtpClient
from email_profile.core.abc import (
    ImapClientProtocol,
    SenderProtocol,
    SmtpClientProtocol,
    StorageABC,
)
from email_profile.core.credentials import Credentials, EmailFactories
from email_profile.core.errors import Retryable
from email_profile.core.status import IMAPError, Status
from email_profile.core.types import AppendedUID, IMAPHost, SMTPHost
from email_profile.mailbox import MailBox
from email_profile.models.email import EmailModel
from email_profile.parser import Attachment, ParsedBody, parse_rfc822
from email_profile.providers import (
    ProviderResolutionError,
    resolve_imap_host,
    resolve_smtp_host,
)
from email_profile.retry import with_retry
from email_profile.searches import Where

__all__ = [
    "AppendedUID",
    "Attachment",
    "Credentials",
    "EmailFactories",
    "EmailModel",
    "IMAPError",
    "IMAPHost",
    "ImapClient",
    "ImapClientProtocol",
    "MailBox",
    "ParsedBody",
    "ProviderResolutionError",
    "Retryable",
    "SMTPHost",
    "SenderProtocol",
    "SmtpClient",
    "SmtpClientProtocol",
    "Status",
    "StorageABC",
    "Where",
    "parse_rfc822",
    "resolve_imap_host",
    "resolve_smtp_host",
    "with_retry",
]
