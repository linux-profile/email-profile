from email_profile import EmailSerializer, MessageDumper, parse_rfc822

MULTIPART_WITH_ATTACHMENT = (
    b"From: alice@example.com\r\n"
    b"To: bob@example.com\r\n"
    b"Subject: Hi\r\n"
    b'Content-Type: multipart/mixed; boundary="BOUNDARY"\r\n\r\n'
    b"--BOUNDARY\r\n"
    b"Content-Type: text/plain; charset=utf-8\r\n\r\n"
    b"plain body\r\n"
    b"--BOUNDARY\r\n"
    b"Content-Type: text/html; charset=utf-8\r\n\r\n"
    b"<p>html body</p>\r\n"
    b"--BOUNDARY\r\n"
    b'Content-Type: text/plain; name="note.txt"\r\n'
    b'Content-Disposition: attachment; filename="note.txt"\r\n\r\n'
    b"hello attachment\r\n"
    b"--BOUNDARY--\r\n"
)


def test_parser_extracts_subject_and_bodies():
    parsed = parse_rfc822(MULTIPART_WITH_ATTACHMENT)
    assert parsed.subject == "Hi"
    assert parsed.body_text_plain.strip() == "plain body"
    assert "<p>html body</p>" in parsed.body_text_html


def test_parser_extracts_attachments():
    parsed = parse_rfc822(MULTIPART_WITH_ATTACHMENT)
    assert len(parsed.attachments) == 1
    a = parsed.attachments[0]
    assert a.file_name == "note.txt"
    assert a.content_type == "text/plain"
    assert b"hello attachment" in a.content


def test_email_serializer_from_raw_carries_parsed_fields():
    msg = EmailSerializer.from_raw(
        uid="42",
        mailbox="INBOX",
        raw=MULTIPART_WITH_ATTACHMENT,
    )
    assert msg.subject == "Hi"
    assert msg.body_text_plain.strip() == "plain body"
    assert len(msg.attachments) == 1


def test_dumper_to_dict_returns_metadata():
    msg = EmailSerializer.from_raw(
        uid="1", mailbox="INBOX", raw=MULTIPART_WITH_ATTACHMENT
    )
    data = MessageDumper(msg).to_dict()
    assert data["subject"] == "Hi"
    assert data["attachments"][0]["file_name"] == "note.txt"


def test_dumper_to_json_writes_file(tmp_path):
    msg = EmailSerializer.from_raw(
        uid="1", mailbox="INBOX", raw=MULTIPART_WITH_ATTACHMENT
    )
    out = MessageDumper(msg).to_json(path=tmp_path)
    assert out.exists()
    assert out.name == f"{msg.id}.json"


def test_dumper_to_html_writes_file(tmp_path):
    msg = EmailSerializer.from_raw(
        uid="1", mailbox="INBOX", raw=MULTIPART_WITH_ATTACHMENT
    )
    out = MessageDumper(msg).to_html(path=tmp_path)
    assert out.exists()
    assert "<p>html body</p>" in out.read_text()


HEADERS_RICH = (
    b"From: alice@example.com\r\n"
    b"To: bob@example.com\r\n"
    b"Subject: Hello\r\n"
    b"Return-Path: <bounces@example.com>\r\n"
    b"Delivered-To: bob@example.com\r\n"
    b"Received: from mta.example.com\r\n"
    b"DKIM-Signature: v=1; a=rsa-sha256; d=example.com; s=sel; b=abc\r\n"
    b"Mime-Version: 1.0\r\n"
    b"Reply-To: support@example.com\r\n"
    b"Precedence: bulk\r\n"
    b"X-SG-EID: eid-123\r\n"
    b"X-SG-ID: id-456\r\n"
    b"X-Entity-ID: entity-789\r\n"
    b"Content-Type: text/plain; charset=utf-8\r\n\r\n"
    b"plain body\r\n"
)


def test_parser_extracts_extended_headers():
    parsed = parse_rfc822(HEADERS_RICH)
    assert parsed.return_path == "<bounces@example.com>"
    assert parsed.delivered_to == "bob@example.com"
    assert "mta.example.com" in parsed.received
    assert "rsa-sha256" in parsed.dkim_signature
    assert parsed.mime_version == "1.0"
    assert parsed.reply_to == "support@example.com"
    assert parsed.precedence == "bulk"
    assert parsed.x_sg_eid == "eid-123"
    assert parsed.x_sg_id == "id-456"
    assert parsed.x_entity_id == "entity-789"
    assert parsed.content_type == "text/plain"


def test_serializer_carries_extended_headers():
    msg = EmailSerializer.from_raw(uid="1", mailbox="INBOX", raw=HEADERS_RICH)
    assert msg.dkim_signature is not None
    assert msg.return_path == "<bounces@example.com>"
    assert msg.precedence == "bulk"


HEADERS_FULL = (
    b"From: alice@example.com\r\n"
    b"To: bob@example.com\r\n"
    b"Cc: carol@example.com, dan@example.com\r\n"
    b"Sender: relay@example.com\r\n"
    b"Reply-To: support@example.com\r\n"
    b"Subject: Newsletter\r\n"
    b"In-Reply-To: <prev-message-id@example.com>\r\n"
    b"References: <root@example.com> <next@example.com>\r\n"
    b"MIME-Version: 1.0\r\n"
    b"Content-Transfer-Encoding: quoted-printable\r\n"
    b"Authentication-Results: mx.google.com; "
    b"spf=pass smtp.mailfrom=example.com\r\n"
    b"ARC-Seal: i=1; a=rsa-sha256; cv=none; d=google.com\r\n"
    b"List-Id: <newsletter.example.com>\r\n"
    b"List-Unsubscribe: <mailto:unsub@example.com>, "
    b"<https://example.com/u>\r\n"
    b"List-Unsubscribe-Post: List-Unsubscribe=One-Click\r\n"
    b"Importance: high\r\n"
    b"X-Priority: 1\r\n"
    b"Auto-Submitted: auto-generated\r\n"
    b"X-Mailer: SuperMail 1.0\r\n"
    b"X-Spam-Flag: NO\r\n"
    b"Comments: please reply by Friday\r\n"
    b"Content-Type: text/plain; charset=utf-8\r\n\r\n"
    b"hi there\r\n"
)


def test_parser_extracts_full_named_set():
    p = parse_rfc822(HEADERS_FULL)
    assert p.cc == "carol@example.com, dan@example.com"
    assert p.sender == "relay@example.com"
    assert p.reply_to == "support@example.com"
    assert p.in_reply_to == "<prev-message-id@example.com>"
    assert "<root@example.com>" in p.references
    assert p.content_transfer_encoding == "quoted-printable"
    assert "spf=pass" in p.authentication_results
    assert "rsa-sha256" in p.arc_seal
    assert p.list_id == "<newsletter.example.com>"
    assert "mailto:unsub" in p.list_unsubscribe
    assert p.list_unsubscribe_post == "List-Unsubscribe=One-Click"
    assert p.importance == "high"
    assert p.x_priority == "1"
    assert p.auto_submitted == "auto-generated"


def test_parser_drops_unknown_into_headers_bag():
    p = parse_rfc822(HEADERS_FULL)
    assert p.headers["X-Mailer"] == "SuperMail 1.0"
    assert p.headers["X-Spam-Flag"] == "NO"
    assert p.headers["Comments"] == "please reply by Friday"
    # Named headers are NOT duplicated in the bag.
    assert "Cc" not in p.headers
    assert "From" not in p.headers


def test_parser_collapses_repeated_headers_into_lists():
    raw = (
        b"From: a@x\r\nTo: b@x\r\nSubject: t\r\n"
        b"Received: from server1\r\n"
        b"Received: from server2\r\n"
        b"X-Custom: one\r\n"
        b"X-Custom: two\r\n"
        b"X-Custom: three\r\n"
        b"\r\nbody\r\n"
    )
    p = parse_rfc822(raw)
    # Received is a named field — single value is the *first* occurrence.
    assert "server1" in p.received
    # Repeated unknown header lands as a list in the bag.
    assert p.headers["X-Custom"] == ["one", "two", "three"]


def test_serializer_exposes_headers_bag():
    msg = EmailSerializer.from_raw(uid="1", mailbox="INBOX", raw=HEADERS_FULL)
    assert msg.cc == "carol@example.com, dan@example.com"
    assert msg.list_id == "<newsletter.example.com>"
    assert msg.headers["X-Mailer"] == "SuperMail 1.0"


HEADERS_ENCODED = (
    b"From: alice@example.com\r\n"
    b"To: bob@example.com\r\n"
    b"Subject: =?utf-8?Q?Ol=C3=A1?=\r\n"
    b"List-Unsubscribe: =?utf-8?Q?<https://example.com/u?eid=abc>?=\r\n"
    b"Content-Type: text/plain\r\n\r\n"
    b"hi\r\n"
)


def test_parser_handles_encoded_headers_without_failing():
    p = parse_rfc822(HEADERS_ENCODED)
    assert isinstance(p.list_unsubscribe, str)
    assert "example.com/u" in p.list_unsubscribe
    assert "Olá" in p.subject


HEADERS_LOWERCASE = (
    b"From: a@x\r\nTo: b@x\r\nSubject: t\r\n"
    b"mime-version: 1.0\r\n"
    b"content-type: text/plain\r\n"
    b"content-transfer-encoding: base64\r\n"
    b"\r\nbody\r\n"
)


def test_named_headers_are_case_insensitive():
    """Hostinger sends `Mime-Version` instead of RFC `MIME-Version`."""
    p = parse_rfc822(HEADERS_LOWERCASE)

    assert p.mime_version == "1.0"
    assert p.content_transfer_encoding == "base64"

    for key in p.headers:
        assert key.lower() not in {
            "mime-version",
            "content-type",
            "content-transfer-encoding",
            "from",
            "to",
            "subject",
        }, f"named header {key!r} leaked into bag"
