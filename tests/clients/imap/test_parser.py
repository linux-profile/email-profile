"""Tests for FetchParser, SearchParser, and EmailParser."""

from hashlib import sha256
from unittest import TestCase

from email_profile.clients.imap.parser import (
    EmailParser,
    FetchParser,
    SearchParser,
)


class TestFetchParserValidation(TestCase):
    def test_is_valid_tuple(self):
        assert FetchParser.is_valid((b"header", b"body"))

    def test_is_valid_rejects_bytes(self):
        assert not FetchParser.is_valid(b")")

    def test_is_valid_rejects_short_tuple(self):
        assert not FetchParser.is_valid((b"only_one",))


class TestFetchParserUid(TestCase):
    def test_parse_uid_from_header(self):
        entry = (b"1 (UID 42 RFC822 {100})", b"body")
        p = FetchParser(entry)
        assert p._parse_uid() == "42"

    def test_parse_uid_returns_none_without_uid(self):
        entry = (b"1 FETCH (FLAGS (\\Seen))", b"body")
        p = FetchParser(entry)
        assert p._parse_uid() is None


class TestFetchParserFlags(TestCase):
    def test_parse_flags_from_header(self):
        entry = (b"1 (UID 10 FLAGS (\\Seen \\Flagged))", b"body")
        p = FetchParser(entry)
        assert p._parse_header_flags() == "\\Seen \\Flagged"

    def test_parse_flags_returns_none_without_flags(self):
        entry = (b"1 (UID 10 RFC822 {100})", b"body")
        p = FetchParser(entry)
        assert p._parse_header_flags() is None

    def test_resolve_flags_from_trailing_bytes(self):
        entry = (b"1 (UID 10 RFC822 {100})", b"body")
        p = FetchParser(entry)
        trailing = b" FLAGS (\\Seen))"
        flags = p._resolve_flags(trailing)
        assert "\\Seen" in flags

    def test_resolve_flags_no_trailing(self):
        entry = (b"1 (UID 10 FLAGS (\\Seen))", b"body")
        p = FetchParser(entry)
        assert p._resolve_flags() == "\\Seen"


class TestFetchParserMessageId(TestCase):
    def test_parse_message_id(self):
        body = b"Message-ID: <abc@example.com>\r\nSubject: Hi\r\n\r\nBody"
        entry = (b"1 (UID 10)", body)
        p = FetchParser(entry)
        assert p._parse_message_id() == "<abc@example.com>"

    def test_parse_message_id_returns_none_without_header(self):
        body = b"Subject: Hi\r\n\r\nBody"
        entry = (b"1 (UID 10)", body)
        p = FetchParser(entry)
        assert p._parse_message_id() is None

    def test_resolve_message_id_uses_header(self):
        body = b"Message-ID: <abc@example.com>\r\nSubject: Hi\r\n\r\nBody"
        entry = (b"1 (UID 10)", body)
        p = FetchParser(entry)
        assert p._resolve_message_id() == "<abc@example.com>"

    def test_resolve_message_id_falls_back_to_hash(self):
        body = b"Subject: Hi\r\n\r\nBody"
        entry = (b"1 (UID 10)", body)
        p = FetchParser(entry)
        expected = sha256(body).hexdigest()
        assert p._resolve_message_id() == expected


class TestFetchParserIterEntries(TestCase):
    def test_iter_entries_yields_parsed(self):
        body = b"Message-ID: <x@y.com>\r\n\r\nHello"
        fetched = [
            (b"1 (UID 100 FLAGS (\\Seen) RFC822 {30})", body),
            b")",
        ]
        entries = list(FetchParser.iter_entries(fetched))
        assert len(entries) == 1
        assert entries[0].uid == "100"
        assert entries[0].flags == "\\Seen"
        assert entries[0].message_id == "<x@y.com>"

    def test_iter_entries_skips_invalid(self):
        fetched = [b")", b"garbage"]
        entries = list(FetchParser.iter_entries(fetched))
        assert len(entries) == 0

    def test_iter_entries_trailing_flags(self):
        body = b"Message-ID: <a@b.com>\r\n\r\nHi"
        fetched = [
            (b"1 (UID 200 RFC822 {20})", body),
            b" FLAGS (\\Flagged))",
        ]
        entries = list(FetchParser.iter_entries(fetched))
        assert len(entries) == 1
        assert "\\Flagged" in entries[0].flags


class TestFetchParserText(TestCase):
    def test_text_decodes_body(self):
        body = b"Subject: Hi\r\n\r\nHello world"
        entry = (b"1 (UID 10)", body)
        p = FetchParser(entry)
        assert "Hello world" in p.text()

    def test_raw_returns_bytes(self):
        body = b"raw bytes"
        entry = (b"1 (UID 10)", body)
        p = FetchParser(entry)
        assert p.raw() == body


class TestParseFlags(TestCase):
    def test_parse_uid_and_flags(self):
        result = FetchParser.parse_flags("UID 10 FLAGS (\\Seen)")
        assert result == ("10", "\\Seen")

    def test_parse_flags_only(self):
        result = FetchParser.parse_flags("FLAGS (\\Seen \\Flagged)")
        assert result == ("", "\\Seen \\Flagged")

    def test_parse_flags_returns_none(self):
        assert FetchParser.parse_flags("no flags here") is None


class TestSearchParser(TestCase):
    def test_parses_uids(self):
        s = SearchParser([b"1 2 3 4"])
        assert s.uids() == ["1", "2", "3", "4"]
        assert s.count() == 4

    def test_empty_data(self):
        s = SearchParser([])
        assert s.uids() == []
        assert s.is_empty()

    def test_empty_bytes(self):
        s = SearchParser([b""])
        assert s.is_empty()

    def test_bool(self):
        assert bool(SearchParser([b"1"]))
        assert not bool(SearchParser([]))

    def test_repr(self):
        s = SearchParser([b"1 2"])
        assert "2" in repr(s)


class TestEmailParser(TestCase):
    def test_subject(self):
        raw = b"Subject: Hello\r\n\r\nBody"
        p = EmailParser(raw)
        assert p.subject() == "Hello"

    def test_from(self):
        raw = b"From: user@example.com\r\n\r\nBody"
        p = EmailParser(raw)
        assert p.from_() == "user@example.com"

    def test_to(self):
        raw = b"To: bob@example.com\r\n\r\nBody"
        p = EmailParser(raw)
        assert p.to() == "bob@example.com"

    def test_message_id(self):
        raw = b"Message-ID: <abc@x.com>\r\n\r\nBody"
        p = EmailParser(raw)
        assert p.message_id() == "<abc@x.com>"

    def test_message_id_or_hash_with_id(self):
        raw = b"Message-ID: <abc@x.com>\r\n\r\nBody"
        p = EmailParser(raw)
        assert p.message_id_or_hash(raw) == "<abc@x.com>"

    def test_message_id_or_hash_without_id(self):
        raw = b"Subject: Hi\r\n\r\nBody"
        p = EmailParser(raw)
        expected = sha256(raw).hexdigest()
        assert p.message_id_or_hash(raw) == expected

    def test_date(self):
        raw = b"Date: Mon, 01 Jan 2024 12:00:00 +0000\r\n\r\nBody"
        p = EmailParser(raw)
        d = p.date()
        assert d is not None
        assert d.year == 2024

    def test_date_returns_none_without_header(self):
        raw = b"Subject: Hi\r\n\r\nBody"
        p = EmailParser(raw)
        assert p.date() is None

    def test_header(self):
        raw = b"X-Custom: foobar\r\n\r\nBody"
        p = EmailParser(raw)
        assert p.header("X-Custom") == "foobar"

    def test_accepts_string(self):
        p = EmailParser("Subject: Hello\r\n\r\nBody")
        assert p.subject() == "Hello"
