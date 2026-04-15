"""IMAP search query model.

Two ways to build a search:

1. Declarative (validated kwargs)::

    Query(subject="hello", unseen=True, since=date(2024, 1, 1))

2. Composable (Q expressions, supports ``&``, ``|``, ``~``)::

    Q.subject("hello") & Q.unseen() & ~Q.from_("spam@x")
"""

from __future__ import annotations

from datetime import date
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field


def _ascii(value: str) -> str:
    return value.encode("ASCII", "ignore").decode()


def _imap_date(value: date) -> str:
    return value.strftime("%d-%b-%Y")


class Query(BaseModel):
    """Validated IMAP search criteria.

    Each non-empty field becomes one IMAP search clause. Empty fields are
    omitted. When every field is empty, :meth:`mount` returns ``"ALL"``.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    since: Optional[date] = None
    before: Optional[date] = None
    on: Optional[date] = None
    sent_since: Optional[date] = None
    sent_before: Optional[date] = None

    subject: Optional[str] = None
    from_who: Optional[str] = Field(default=None, alias="from")
    to: Optional[str] = None
    cc: Optional[str] = None
    bcc: Optional[str] = None

    body: Optional[str] = None
    text: Optional[str] = None
    keyword: Optional[str] = None

    larger: Optional[int] = None
    smaller: Optional[int] = None

    seen: Optional[bool] = None
    answered: Optional[bool] = None
    flagged: Optional[bool] = None
    deleted: Optional[bool] = None
    draft: Optional[bool] = None

    unseen: bool = False

    def _date_clauses(self) -> list[str]:
        fields = (
            ("SINCE", self.since),
            ("BEFORE", self.before),
            ("ON", self.on),
            ("SENTSINCE", self.sent_since),
            ("SENTBEFORE", self.sent_before),
        )
        return [
            f"({name} {_imap_date(value)})" for name, value in fields if value
        ]

    def _string_clauses(self) -> list[str]:
        fields = (
            ("SUBJECT", self.subject),
            ("FROM", self.from_who),
            ("TO", self.to),
            ("CC", self.cc),
            ("BCC", self.bcc),
            ("BODY", self.body),
            ("TEXT", self.text),
            ("KEYWORD", self.keyword),
        )
        return [
            f'({name} "{_ascii(value)}")' for name, value in fields if value
        ]

    def _size_clauses(self) -> list[str]:
        fields = (("LARGER", self.larger), ("SMALLER", self.smaller))
        return [
            f"({name} {value})" for name, value in fields if value is not None
        ]

    def _flag_clauses(self) -> list[str]:
        fields = (
            (self.seen, "SEEN"),
            (self.answered, "ANSWERED"),
            (self.flagged, "FLAGGED"),
            (self.deleted, "DELETED"),
            (self.draft, "DRAFT"),
        )
        parts: list[str] = []
        for flag, name in fields:
            if flag is True:
                parts.append(f"({name})")
            elif flag is False:
                parts.append(f"(UN{name})")
        if self.unseen:
            parts.append("(UNSEEN)")
        return parts

    def _clauses(self) -> list[str]:
        return (
            self._date_clauses()
            + self._string_clauses()
            + self._size_clauses()
            + self._flag_clauses()
        )

    def mount(self) -> str:
        """Render this query as an IMAP search criteria string."""
        parts = self._clauses()
        return " ".join(parts) if parts else "ALL"

    def __and__(self, other: QueryLike) -> Q:
        return Q(self.mount()) & _q(other)

    def __or__(self, other: QueryLike) -> Q:
        return Q(self.mount()) | _q(other)

    def __invert__(self) -> Q:
        return ~Q(self.mount())


class Q:
    """Composable IMAP search expression. Supports ``&``, ``|``, ``~``."""

    __slots__ = ("_expr",)

    def __init__(self, expr: str) -> None:
        self._expr = expr

    def mount(self) -> str:
        return self._expr or "ALL"

    def __and__(self, other: QueryLike) -> Q:
        right = _q(other)._expr
        return Q(f"{self._expr} {right}".strip())

    def __or__(self, other: QueryLike) -> Q:
        right = _q(other)._expr
        return Q(f"OR {self._expr} {right}".strip())

    def __invert__(self) -> Q:
        return Q(f"NOT {self._expr}")

    def __repr__(self) -> str:
        return f"Q({self._expr!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Q) and self._expr == other._expr

    def __hash__(self) -> int:
        return hash(self._expr)

    @staticmethod
    def subject(value: str) -> Q:
        return Q(f'(SUBJECT "{_ascii(value)}")')

    @staticmethod
    def from_(value: str) -> Q:
        return Q(f'(FROM "{_ascii(value)}")')

    @staticmethod
    def to(value: str) -> Q:
        return Q(f'(TO "{_ascii(value)}")')

    @staticmethod
    def cc(value: str) -> Q:
        return Q(f'(CC "{_ascii(value)}")')

    @staticmethod
    def body(value: str) -> Q:
        return Q(f'(BODY "{_ascii(value)}")')

    @staticmethod
    def text(value: str) -> Q:
        return Q(f'(TEXT "{_ascii(value)}")')

    @staticmethod
    def since(value: date) -> Q:
        return Q(f"(SINCE {_imap_date(value)})")

    @staticmethod
    def before(value: date) -> Q:
        return Q(f"(BEFORE {_imap_date(value)})")

    @staticmethod
    def on(value: date) -> Q:
        return Q(f"(ON {_imap_date(value)})")

    @staticmethod
    def larger(n: int) -> Q:
        return Q(f"(LARGER {n})")

    @staticmethod
    def smaller(n: int) -> Q:
        return Q(f"(SMALLER {n})")

    @staticmethod
    def unseen() -> Q:
        return Q("(UNSEEN)")

    @staticmethod
    def seen() -> Q:
        return Q("(SEEN)")

    @staticmethod
    def answered() -> Q:
        return Q("(ANSWERED)")

    @staticmethod
    def flagged() -> Q:
        return Q("(FLAGGED)")

    @staticmethod
    def all() -> Q:
        return Q("ALL")


QueryLike = Union[Query, Q, str]


def _q(value: QueryLike) -> Q:
    if isinstance(value, Q):
        return value
    if isinstance(value, Query):
        return Q(value.mount())
    if isinstance(value, str):
        return Q(value)
    raise TypeError(f"Cannot use {type(value).__name__} as a query")
