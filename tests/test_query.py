from datetime import date

import pytest
from pydantic import ValidationError

from email_profile import Q, Query


def test_empty_query_mounts_all():
    assert Query().mount() == "ALL"


def test_subject_clause():
    assert Query(subject="hello").mount() == '(SUBJECT "hello")'


def test_combined_clauses_use_imap_date_format():
    q = Query(
        since=date(2030, 1, 1), before=date(2030, 12, 31), from_who="a@b"
    )
    out = q.mount()
    assert "(SINCE 01-Jan-2030)" in out
    assert "(BEFORE 31-Dec-2030)" in out
    assert '(FROM "a@b")' in out


def test_from_alias_accepts_from_keyword():
    q = Query(**{"from": "a@b"})
    assert '(FROM "a@b")' in q.mount()


def test_flag_filters_render_seen_unseen_correctly():
    assert Query(seen=True).mount() == "(SEEN)"
    assert Query(seen=False).mount() == "(UNSEEN)"
    assert Query(answered=False).mount() == "(UNANSWERED)"


def test_size_filters():
    out = Query(larger=1024, smaller=4096).mount()
    assert "(LARGER 1024)" in out
    assert "(SMALLER 4096)" in out


def test_invalid_since_type_rejected():
    with pytest.raises(ValidationError):
        Query(since="yesterday")


def test_extra_field_rejected():
    with pytest.raises(ValidationError):
        Query(unknown="x")


def test_q_combinators_and_or_not():
    expr = (Q.subject("hi") & Q.unseen()).mount()
    assert "(SUBJECT" in expr and "(UNSEEN)" in expr

    expr = (Q.subject("a") | Q.subject("b")).mount()
    assert expr.startswith("OR ")

    expr = (~Q.unseen()).mount()
    assert expr == "NOT (UNSEEN)"


def test_query_can_be_combined_with_q():
    expr = (Query(subject="hi") & Q.unseen()).mount()
    assert "(SUBJECT" in expr and "(UNSEEN)" in expr
