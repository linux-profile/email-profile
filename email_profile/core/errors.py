"""Custom exceptions raised by the public API."""

from __future__ import annotations


class ConnectionFailure(Exception):
    """Raised when the IMAP login fails."""

    def __init__(self) -> None:
        super().__init__("Failed to connect to email server.")


class NotConnected(RuntimeError):
    """Raised when a connection-bound method is called too early."""

    def __init__(self) -> None:
        super().__init__(
            "Email client is not connected. Call .connect() or use a `with` block."
        )


class QuotaExceeded(Exception):
    """Raised when the server reports the account is over its storage quota."""


class RateLimited(Exception):
    """Raised when the server reports a bandwidth or rate limit hit."""


class Retryable(Exception):
    """Raised when an operation hit a transient failure worth retrying."""
