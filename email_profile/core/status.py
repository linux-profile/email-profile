"""IMAP status validation."""

from __future__ import annotations

from dataclasses import dataclass

from email_profile.core.errors import IMAPError, QuotaExceeded, RateLimited


@dataclass
class StatusResponse:
    ok: bool
    message: str


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


_STATUS_MESSAGES = {
    "OK": (True, "Command completed successfully"),
    "NO": (False, "Command failed"),
    "BAD": (False, "Command unknown or arguments invalid"),
}


class Status:
    OK = "OK"
    NO = "NO"
    BAD = "BAD"

    @staticmethod
    def check_status(status: str) -> StatusResponse:
        """Return a StatusResponse without raising on failure."""
        ok, message = _STATUS_MESSAGES.get(status, (False, "Unknown error"))
        return StatusResponse(ok=ok, message=message)

    @staticmethod
    def validate_status(
        status: str,
        payload: object = None,
    ) -> StatusResponse:
        """Return a StatusResponse, raising on failure."""
        ok, message = _STATUS_MESSAGES.get(status, (False, "Unknown error"))

        if not ok:
            specific = _classify(payload)
            if specific is not None:
                raise specific
            raise IMAPError(message)

        return StatusResponse(ok=ok, message=message)

    @staticmethod
    def state(context: tuple) -> list:
        """Validate IMAP response and return the payload."""
        Status.validate_status(context[0], payload=context[1])
        return context[1]
