from datetime import date
from unittest import TestCase

from pydantic import ValidationError

from email_profile import Q, Query


class TestQuery(TestCase):
    def test_empty_mounts_all(self):
        self.assertEqual(Query().mount(), "ALL")

    def test_subject(self):
        self.assertEqual(Query(subject="hi").mount(), '(SUBJECT "hi")')

    def test_from_alias(self):
        self.assertIn('(FROM "a@b")', Query(**{"from": "a@b"}).mount())

    def test_date_format(self):
        out = Query(since=date(2030, 1, 1), before=date(2030, 12, 31)).mount()
        self.assertIn("(SINCE 01-Jan-2030)", out)
        self.assertIn("(BEFORE 31-Dec-2030)", out)

    def test_flags(self):
        self.assertEqual(Query(seen=True).mount(), "(SEEN)")
        self.assertEqual(Query(seen=False).mount(), "ALL")
        self.assertEqual(Query(answered=True).mount(), "(ANSWERED)")
        self.assertEqual(Query(answered=False).mount(), "ALL")
        self.assertEqual(Query(unseen=True).mount(), "(UNSEEN)")
        self.assertEqual(Query(unseen=False).mount(), "ALL")

    def test_contradictory_seen_unseen_rejected(self):
        with self.assertRaises(ValidationError):
            Query(seen=True, unseen=True)

    def test_size_filters(self):
        out = Query(larger=1024, smaller=4096).mount()
        self.assertIn("(LARGER 1024)", out)
        self.assertIn("(SMALLER 4096)", out)

    def test_invalid_type_rejected(self):
        with self.assertRaises(ValidationError):
            Query(since="yesterday")

    def test_extra_field_rejected(self):
        with self.assertRaises(ValidationError):
            Query(unknown="x")


class TestQ(TestCase):
    def test_combinators(self):
        self.assertIn("(SUBJECT", (Q.subject("a") & Q.unseen()).mount())
        self.assertTrue(
            (Q.subject("a") | Q.subject("b")).mount().startswith("OR ")
        )
        self.assertEqual((~Q.unseen()).mount(), "NOT (UNSEEN)")

    def test_query_combines_with_q(self):
        expr = (Query(subject="a") & Q.unseen()).mount()
        self.assertIn("(SUBJECT", expr)
        self.assertIn("(UNSEEN)", expr)


class TestOrNotArity(TestCase):
    def test_or_groups_multi_clause_operands(self):
        expr = (
            Query(subject="x", unseen=True) | Query(from_who="a@b")
        ).mount()
        self.assertEqual(expr, 'OR ((SUBJECT "x") (UNSEEN)) (FROM "a@b")')

    def test_invert_groups_multi_clause(self):
        expr = (~Query(subject="x", unseen=True)).mount()
        self.assertEqual(expr, 'NOT ((SUBJECT "x") (UNSEEN))')

    def test_exclude_groups_multi_clause(self):
        expr = (
            Query(subject="report")
            .exclude(from_who="spam@x", unseen=True)
            .mount()
        )
        self.assertIn('NOT ((FROM "spam@x") (UNSEEN))', expr)
        self.assertIn('(SUBJECT "report")', expr)

    def test_or_method_groups_multi_clause(self):
        expr = Query(subject="a").or_(from_who="b@x", unseen=True).mount()
        self.assertEqual(expr, 'OR (SUBJECT "a") ((FROM "b@x") (UNSEEN))')

    def test_or_keeps_single_clause_unwrapped(self):
        expr = (Q.subject("a") | Q.subject("b")).mount()
        self.assertEqual(expr, 'OR (SUBJECT "a") (SUBJECT "b")')
