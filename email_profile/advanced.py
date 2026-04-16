"""Advanced / power-user symbols."""

from __future__ import annotations

from email_profile.clients.imap.client import ImapClient
from email_profile.clients.imap.mailbox import MailBox
from email_profile.clients.imap.where import Where
from email_profile.clients.smtp.client import SmtpClient
from email_profile.core.abc import (
    ImapClientABC,
    SenderABC,
    SmtpClientABC,
    StorageABC,
)
from email_profile.core.credentials import Credentials, EmailFactories
from email_profile.core.errors import IMAPError, Retryable
from email_profile.core.status import Status
from email_profile.core.types import AppendedUID, IMAPHost, SMTPHost
from email_profile.models.raw import RawModel
from email_profile.parser import Attachment, ParsedBody, parse_rfc822
from email_profile.providers import (
    ProviderResolutionError,
    resolve_imap_host,
    resolve_smtp_host,
)
from email_profile.retry import with_retry

__all__ = [
    "AppendedUID",
    "Attachment",
    "Credentials",
    "EmailFactories",
    "IMAPError",
    "IMAPHost",
    "ImapClient",
    "ImapClientABC",
    "MailBox",
    "ParsedBody",
    "ProviderResolutionError",
    "RawModel",
    "Retryable",
    "SMTPHost",
    "SenderABC",
    "SmtpClient",
    "SmtpClientABC",
    "Status",
    "StorageABC",
    "Where",
    "parse_rfc822",
    "resolve_imap_host",
    "resolve_smtp_host",
    "with_retry",
]
