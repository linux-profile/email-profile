__version__ = "0.6.0"

__author__ = "Fernando Celmer <email@fernandocelmer.com>"
__copyright__ = """MIT License

Copyright (c) 2024 Email Profile

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

from email_profile.dump import MessageDumper
from email_profile.email import Email
from email_profile.eml import EmailModel, EmailSerializer
from email_profile.errors import (
    ConnectionFailure,
    NotConnected,
    QuotaExceeded,
    RateLimited,
    Retryable,
)
from email_profile.mailbox import AppendedUID, MailBox
from email_profile.parser import Attachment, ParsedBody, parse_rfc822
from email_profile.protocols import StorageProtocol
from email_profile.providers import (
    IMAPHost,
    ProviderResolutionError,
    resolve_imap_host,
)
from email_profile.query import Q, Query
from email_profile.retry import with_retry
from email_profile.searches import Where
from email_profile.status import IMAPError, Status
from email_profile.storage import Storage

__all__ = [
    "AppendedUID",
    "Attachment",
    "ConnectionFailure",
    "Email",
    "EmailModel",
    "EmailSerializer",
    "IMAPError",
    "IMAPHost",
    "MailBox",
    "MessageDumper",
    "NotConnected",
    "ParsedBody",
    "ProviderResolutionError",
    "Q",
    "Query",
    "QuotaExceeded",
    "RateLimited",
    "Retryable",
    "Status",
    "Storage",
    "StorageProtocol",
    "Where",
    "parse_rfc822",
    "resolve_imap_host",
    "with_retry",
]
