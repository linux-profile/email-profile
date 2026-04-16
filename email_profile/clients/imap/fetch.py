"""IMAP fetch spec builder.

Composable fetch specifications for IMAP FETCH commands::

    F.rfc822()                          # full email
    F.flags()                           # just flags
    F.header("Message-ID")             # single header
    F.headers("From", "Subject")       # multiple headers
    F.body_text()                       # headers + body, no attachments
    F.rfc822() + F.flags()             # combine specs
"""

from __future__ import annotations


class F:
    """Composable IMAP fetch specification."""

    __slots__ = ("_spec",)

    def __init__(self, spec: str) -> None:
        self._spec = spec

    def mount(self) -> str:
        return self._spec

    def __add__(self, other: F) -> F:
        left = self._spec.strip("()")
        right = other._spec.strip("()")
        return F(f"({left} {right})")

    def __repr__(self) -> str:
        return f"F({self._spec!r})"

    @staticmethod
    def rfc822() -> F:
        return F("(RFC822)")

    @staticmethod
    def flags() -> F:
        return F("(FLAGS)")

    @staticmethod
    def all_headers() -> F:
        return F("(BODY.PEEK[HEADER])")

    @staticmethod
    def header(name: str) -> F:
        return F(f"(BODY.PEEK[HEADER.FIELDS ({name.upper()})])")

    @staticmethod
    def headers(*names: str) -> F:
        fields = " ".join(n.upper() for n in names)
        return F(f"(BODY.PEEK[HEADER.FIELDS ({fields})])")

    @staticmethod
    def body_text() -> F:
        return F("(BODY.PEEK[HEADER] BODY.PEEK[TEXT])")

    @staticmethod
    def body_peek() -> F:
        return F("(BODY.PEEK[])")

    @staticmethod
    def envelope() -> F:
        return F("(ENVELOPE)")

    @staticmethod
    def size() -> F:
        return F("(RFC822.SIZE)")
