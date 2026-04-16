"""Tests for the F fetch spec builder."""

from unittest import TestCase

from email_profile.clients.imap.fetch import F


class TestFSpec(TestCase):
    def test_rfc822(self):
        assert F.rfc822().mount() == "(RFC822)"

    def test_flags(self):
        assert F.flags().mount() == "(FLAGS)"

    def test_all_headers(self):
        assert F.all_headers().mount() == "(BODY.PEEK[HEADER])"

    def test_header_single(self):
        spec = F.header("Message-ID").mount()
        assert "HEADER.FIELDS" in spec
        assert "MESSAGE-ID" in spec

    def test_headers_multiple(self):
        spec = F.headers("From", "Subject").mount()
        assert "FROM" in spec
        assert "SUBJECT" in spec

    def test_body_text(self):
        spec = F.body_text().mount()
        assert "BODY.PEEK[HEADER]" in spec
        assert "BODY.PEEK[TEXT]" in spec

    def test_body_peek(self):
        assert F.body_peek().mount() == "(BODY.PEEK[])"

    def test_envelope(self):
        assert F.envelope().mount() == "(ENVELOPE)"

    def test_size(self):
        assert F.size().mount() == "(RFC822.SIZE)"

    def test_composition(self):
        spec = (F.rfc822() + F.flags()).mount()
        assert "RFC822" in spec
        assert "FLAGS" in spec
        assert spec.startswith("(")
        assert spec.endswith(")")

    def test_repr(self):
        assert "RFC822" in repr(F.rfc822())
