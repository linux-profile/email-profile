from unittest import TestCase

from email_profile.parser import parse_rfc822

MULTIPART = (
    b"From: a@x\r\n"
    b"To: b@x\r\n"
    b"Subject: Hi\r\n"
    b'Content-Type: multipart/mixed; boundary="B"\r\n\r\n'
    b"--B\r\nContent-Type: text/plain\r\n\r\nplain body\r\n"
    b"--B\r\nContent-Type: text/html\r\n\r\n<p>html body</p>\r\n"
    b'--B\r\nContent-Disposition: attachment; filename="note.txt"\r\n\r\n'
    b"hello attachment\r\n"
    b"--B--\r\n"
)


class TestSubjectAndBodies(TestCase):
    def test_subject(self):
        self.assertEqual(parse_rfc822(MULTIPART).subject, "Hi")

    def test_plain_body(self):
        self.assertEqual(
            parse_rfc822(MULTIPART).body_text_plain.strip(), "plain body"
        )

    def test_html_body(self):
        self.assertIn(
            "<p>html body</p>", parse_rfc822(MULTIPART).body_text_html
        )


class TestAttachments(TestCase):
    def test_count_and_name(self):
        atts = parse_rfc822(MULTIPART).attachments
        self.assertEqual(len(atts), 1)
        self.assertEqual(atts[0].file_name, "note.txt")

    def test_content(self):
        self.assertIn(
            b"hello attachment", parse_rfc822(MULTIPART).attachments[0].content
        )


class TestAttachmentPathTraversal(TestCase):
    def _msg(self, filename: str) -> bytes:
        return (
            b"From: a@x\r\nTo: b@x\r\nSubject: t\r\n"
            b'Content-Type: multipart/mixed; boundary="B"\r\n\r\n'
            b"--B\r\nContent-Type: text/plain\r\n\r\nbody\r\n"
            b"--B\r\nContent-Disposition: attachment; "
            b'filename="' + filename.encode() + b'"\r\n\r\n'
            b"payload\r\n--B--\r\n"
        )

    def test_unix_traversal_stripped(self):
        atts = parse_rfc822(self._msg("../../etc/passwd")).attachments
        self.assertEqual(len(atts), 1)
        self.assertEqual(atts[0].file_name, "passwd")

    def test_windows_traversal_stripped(self):
        atts = parse_rfc822(
            self._msg("..\\\\..\\\\windows\\\\evil.exe")
        ).attachments
        self.assertEqual(atts[0].file_name, "evil.exe")

    def test_pure_traversal_dropped(self):
        self.assertEqual(parse_rfc822(self._msg("../..")).attachments, [])


class TestNamedHeaders(TestCase):
    def test_named_headers_extracted(self):
        raw = (
            b"From: a@x\r\nTo: b@x\r\nSubject: t\r\n"
            b"Cc: c@x\r\nBcc: d@x\r\nSender: r@x\r\nReply-To: s@x\r\n"
            b"In-Reply-To: <prev@x>\r\nReferences: <root@x>\r\n"
            b"DKIM-Signature: v=1\r\nList-Id: <list@x>\r\n"
            b"List-Unsubscribe: <mailto:u@x>\r\n"
            b"Importance: high\r\nAuto-Submitted: auto\r\n"
            b"Content-Type: text/plain\r\n\r\nbody\r\n"
        )
        p = parse_rfc822(raw)
        self.assertEqual(p.cc, "c@x")
        self.assertEqual(p.in_reply_to, "<prev@x>")
        self.assertEqual(p.list_id, "<list@x>")
        self.assertEqual(p.headers["Importance"], "high")

    def test_case_insensitive(self):
        raw = (
            b"From: a@x\r\nTo: b@x\r\nSubject: t\r\n"
            b"mime-version: 1.0\r\ncontent-type: text/plain\r\n\r\nbody\r\n"
        )
        p = parse_rfc822(raw)
        self.assertIn("mime-version", (k.lower() for k in p.headers))


class TestHeadersBag(TestCase):
    def test_unknown_headers_go_to_bag(self):
        raw = (
            b"From: a@x\r\nTo: b@x\r\nSubject: t\r\n"
            b"X-Mailer: Foo\r\nX-Spam-Flag: NO\r\n\r\nbody\r\n"
        )
        p = parse_rfc822(raw)
        self.assertEqual(p.headers["X-Mailer"], "Foo")
        self.assertEqual(p.headers["X-Spam-Flag"], "NO")
        self.assertNotIn("From", p.headers)

    def test_repeated_headers_collapse_to_list(self):
        raw = (
            b"From: a@x\r\nTo: b@x\r\nSubject: t\r\n"
            b"X-Custom: 1\r\nX-Custom: 2\r\nX-Custom: 3\r\n\r\nbody\r\n"
        )
        result = parse_rfc822(raw).headers["X-Custom"]
        self.assertEqual(result, ["1", "2", "3"])

    def test_encoded_headers_dont_break(self):
        raw = (
            b"From: a@x\r\nTo: b@x\r\n"
            b"Subject: =?utf-8?Q?Ol=C3=A1?=\r\n"
            b"List-Unsubscribe: =?utf-8?Q?<https://x.com/u>?=\r\n"
            b"Content-Type: text/plain\r\n\r\nbody\r\n"
        )
        p = parse_rfc822(raw)
        self.assertIn("Olá", p.subject)
        self.assertIsInstance(p.list_unsubscribe, str)
