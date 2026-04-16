"""IMAP status validation."""

from __future__ import annotations

from email_profile.core.errors import QuotaExceeded, RateLimited


class IMAPError(Exception):
    """Raised when the IMAP server returns a non-OK status."""


class StatusResponse:
    def __init__(self, ok: bool, message: str) -> None:
        self.ok = ok
        self.message = message

    @property
    def type(self) -> bool:
        return self.ok


_QUOTA_HINTS = ("OVERQUOTA", "QUOTA-EXCEEDED", "TOO MUCH MAIL")
_RATE_HINTS = (
    "BANDWIDTH-LIMIT",
    "BANDWIDTH",
    "TOO MANY",
    "RATE",
    "TRYAGAIN",
    "TEMPFAIL",
)


def _classify(payload: object) -> Exception | None:
    """Detect quota/rate-limit hints in an IMAP response payload."""
    text = ""
    if isinstance(payload, list):
        for chunk in payload:
            if isinstance(chunk, bytes):
                text += chunk.decode("utf-8", errors="replace") + " "
            else:
                text += str(chunk) + " "
    else:
        text = str(payload or "")

    upper = text.upper()
    for hint in _QUOTA_HINTS:
        if hint in upper:
            return QuotaExceeded(text.strip())
    for hint in _RATE_HINTS:
        if hint in upper:
            return RateLimited(text.strip())
    return None


class Status:
    OK = "OK"
    NO = "NO"
    BAD = "BAD"

    _MESSAGES = {
        OK: (True, "Login completed, now in authenticated state"),
        NO: (False, "Login failure: user name or password rejected"),
        BAD: (False, "Command unknown or arguments invalid"),
    }

    @staticmethod
    def check_status(
        status: str,
    ) -> StatusResponse:
        """Return a StatusResponse without raising on failure."""
        ok, message = Status._MESSAGES.get(status, (False, "Unknown error"))
        return StatusResponse(ok=ok, message=message)

    @staticmethod
    def validate_status(
        status: str,
        payload: object = None,
    ) -> StatusResponse:
        """Return a StatusResponse, raising on failure."""
        ok, message = Status._MESSAGES.get(status, (False, "Unknown error"))
        if not ok:
            specific = _classify(payload)
            if specific is not None:
                raise specific
            raise IMAPError(message)
        return StatusResponse(ok=ok, message=message)

    @staticmethod
    def validate_data(data: list[bytes]) -> list[str]:
        if not data or data[0] is None:
            return []
        items = [x.decode() for x in data[0].split()]
        if len(items) == 1 and not items[0]:
            return []
        return items
