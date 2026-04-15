"""IMAP status validation."""

from __future__ import annotations


class IMAPError(Exception):
    """Raised when the IMAP server returns a non-OK status."""


class StatusResponse:
    def __init__(self, ok: bool, message: str) -> None:
        self.ok = ok
        self.message = message

    @property
    def type(self) -> bool:  # legacy alias
        return self.ok


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
    def validate_status(
        status: str, raise_error: bool = True
    ) -> StatusResponse:
        ok, message = Status._MESSAGES.get(status, (False, "Unknown error"))
        if raise_error and not ok:
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
