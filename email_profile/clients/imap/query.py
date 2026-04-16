"""IMAP search query builder.

Build searches with validated kwargs or composable expressions::

    Query(subject="hello", unseen=True, since=date(2024, 1, 1))

    Query.where.subject("hello") & Query.where.unseen()

    Query(subject="test").exclude(from_="spam").or_(subject="urgent")
"""

from __future__ import annotations

from datetime import date
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field


def _ascii(value: str) -> str:
    return value.encode("ASCII", "ignore").decode()


def _imap_date(value: date) -> str:
    return value.strftime("%d-%b-%Y")


class _Expr:
    """Internal composable IMAP search expression."""

    __slots__ = ("_expr",)

    def __init__(self, expr: str) -> None:
        self._expr = expr

    def mount(self) -> str:
        return self._expr or "ALL"

    def exclude(self, **kwargs: object) -> _Expr:
        return self & ~_Expr(Query(**kwargs).mount())

    def or_(self, **kwargs: object) -> _Expr:
        return self | _Expr(Query(**kwargs).mount())

    def __and__(self, other: QueryLike) -> _Expr:
        right = _to_expr(other)._expr
        return _Expr(f"{self._expr} {right}".strip())

    def __or__(self, other: QueryLike) -> _Expr:
        right = _to_expr(other)._expr
        return _Expr(f"OR {self._expr} {right}".strip())

    def __invert__(self) -> _Expr:
        return _Expr(f"NOT {self._expr}")

    def __repr__(self) -> str:
        return f"_Expr({self._expr!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _Expr) and self._expr == other._expr

    def __hash__(self) -> int:
        return hash(self._expr)


class Q:
    """Composable query expressions for IMAP search."""

    @staticmethod
    def subject(value: str) -> _Expr:
        return _Expr(f'(SUBJECT "{_ascii(value)}")')

    @staticmethod
    def from_(value: str) -> _Expr:
        return _Expr(f'(FROM "{_ascii(value)}")')

    @staticmethod
    def to(value: str) -> _Expr:
        return _Expr(f'(TO "{_ascii(value)}")')

    @staticmethod
    def cc(value: str) -> _Expr:
        return _Expr(f'(CC "{_ascii(value)}")')

    @staticmethod
    def body(value: str) -> _Expr:
        return _Expr(f'(BODY "{_ascii(value)}")')

    @staticmethod
    def text(value: str) -> _Expr:
        return _Expr(f'(TEXT "{_ascii(value)}")')

    @staticmethod
    def since(value: date) -> _Expr:
        return _Expr(f"(SINCE {_imap_date(value)})")

    @staticmethod
    def before(value: date) -> _Expr:
        return _Expr(f"(BEFORE {_imap_date(value)})")

    @staticmethod
    def on(value: date) -> _Expr:
        return _Expr(f"(ON {_imap_date(value)})")

    @staticmethod
    def larger(n: int) -> _Expr:
        return _Expr(f"(LARGER {n})")

    @staticmethod
    def smaller(n: int) -> _Expr:
        return _Expr(f"(SMALLER {n})")

    @staticmethod
    def unseen() -> _Expr:
        return _Expr("(UNSEEN)")

    @staticmethod
    def seen() -> _Expr:
        return _Expr("(SEEN)")

    @staticmethod
    def answered() -> _Expr:
        return _Expr("(ANSWERED)")

    @staticmethod
    def flagged() -> _Expr:
        return _Expr("(FLAGGED)")

    @staticmethod
    def deleted() -> _Expr:
        return _Expr("(DELETED)")

    @staticmethod
    def undeleted() -> _Expr:
        return _Expr("(UNDELETED)")

    @staticmethod
    def all() -> _Expr:
        return _Expr("ALL")

    @staticmethod
    def uid(value: str) -> _Expr:
        return _Expr(f"UID {value}")

    @staticmethod
    def uid_set(uids: list[str]) -> _Expr:
        return _Expr(f"UID {','.join(uids)}")

    @staticmethod
    def header(name: str, value: str) -> _Expr:
        return _Expr(f'(HEADER {name} "{_ascii(value)}")')


class Query(BaseModel):
    """IMAP search query builder.

    Use kwargs for simple queries::

        Query(subject="hello", unseen=True)

    Use ``Query.where`` for composable expressions::

        Query.where.subject("hello") & Query.where.unseen()

    Chain with ``.exclude()`` and ``.or_()``::

        Query(subject="report").exclude(from_="spam").or_(subject="urgent")
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

    unseen: Optional[bool] = None

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
        if self.unseen is True:
            parts.append("(UNSEEN)")
        elif self.unseen is False:
            parts.append("(SEEN)")
        return parts

    def _clauses(self) -> list[str]:
        return (
            self._date_clauses()
            + self._string_clauses()
            + self._size_clauses()
            + self._flag_clauses()
        )

    def mount(self) -> str:
        parts = self._clauses()
        return " ".join(parts) if parts else "ALL"

    def exclude(self, **kwargs: object) -> _Expr:
        return _Expr(self.mount()) & ~_Expr(Query(**kwargs).mount())

    def or_(self, **kwargs: object) -> _Expr:
        return _Expr(self.mount()) | _Expr(Query(**kwargs).mount())

    def __and__(self, other: QueryLike) -> _Expr:
        return _Expr(self.mount()) & _to_expr(other)

    def __or__(self, other: QueryLike) -> _Expr:
        return _Expr(self.mount()) | _to_expr(other)

    def __invert__(self) -> _Expr:
        return ~_Expr(self.mount())


QueryLike = Union[Query, Q, _Expr, str]


def _to_expr(value: QueryLike) -> _Expr:
    if isinstance(value, _Expr):
        return value
    if isinstance(value, Query):
        return _Expr(value.mount())
    if isinstance(value, str):
        return _Expr(value)
    raise TypeError(f"Cannot use {type(value).__name__} as a query")
