import tempfile
from email.message import EmailMessage
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from email_profile.clients.smtp.client import (
    MAX_ATTACHMENT_SIZE,
    SmtpClient,
    _attach,
    _build_message,
)
from email_profile.core.types import SMTPHost


class TestBuildMessage(TestCase):
    def test_basic_text(self):
        msg = _build_message(
            sender="me@x", to="you@x", subject="hi", body="hello"
        )
        self.assertEqual(msg["From"], "me@x")
        self.assertEqual(msg["To"], "you@x")
        self.assertEqual(msg["Subject"], "hi")
        self.assertIn("hello", msg.get_content())

    def test_html_alternative(self):
        msg = _build_message(
            sender="me@x",
            to="you@x",
            subject="hi",
            body="plain",
            html="<p>html</p>",
        )
        self.assertTrue(msg.is_multipart())

    def test_list_recipients_joined(self):
        msg = _build_message(
            sender="me@x",
            to=["a@x", "b@x"],
            subject="hi",
            cc=["c@x"],
        )
        self.assertEqual(msg["To"], "a@x, b@x")
        self.assertEqual(msg["Cc"], "c@x")

    def test_custom_headers(self):
        msg = _build_message(
            sender="me@x",
            to="you@x",
            subject="hi",
            headers={"In-Reply-To": "<prev@x>"},
        )
        self.assertEqual(msg["In-Reply-To"], "<prev@x>")

    def test_attachment_from_bytes_tuple(self):
        msg = _build_message(
            sender="me@x",
            to="you@x",
            subject="hi",
            attachments=[("note.txt", b"hello")],
        )
        parts = list(msg.iter_attachments())
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0].get_filename(), "note.txt")


class TestSmtpClientSSL(TestCase):
    def setUp(self):
        self.host = SMTPHost("smtp.x", port=465, ssl=True)
        self.fake = MagicMock()
        self._patcher = patch(
            "email_profile.clients.smtp.client.smtplib.SMTP_SSL",
            return_value=self.fake,
        )
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_connect_logs_in(self):
        SmtpClient(host=self.host, user="u", password="pw").connect()
        self.fake.login.assert_called_once_with("u", "pw")

    def test_context_manager_quits(self):
        with SmtpClient(host=self.host, user="u", password="pw") as client:
            self.assertTrue(client.is_connected)
        self.fake.quit.assert_called_once()

    def test_send_delegates_to_send_message(self):
        msg = EmailMessage()
        with SmtpClient(host=self.host, user="u", password="pw") as client:
            client.send(msg)
        self.fake.send_message.assert_called_once_with(msg)


class TestSmtpClientStartTLS(TestCase):
    def test_starttls_upgrades(self):
        host = SMTPHost("smtp.x", port=587, ssl=False, starttls=True)
        fake = MagicMock()
        with patch(
            "email_profile.clients.smtp.client.smtplib.SMTP", return_value=fake
        ):
            SmtpClient(host=host, user="u", password="pw").connect()
        fake.starttls.assert_called_once()
        fake.login.assert_called_once_with("u", "pw")


class TestAttachmentSizeValidation(TestCase):
    def test_bytes_tuple_exceeds_limit(self):
        msg = EmailMessage()
        big = b"x" * (MAX_ATTACHMENT_SIZE + 1)
        with self.assertRaises(ValueError) as ctx:
            _attach(msg, ("big.bin", big))
        self.assertIn("big.bin", str(ctx.exception))
        self.assertIn("exceeds", str(ctx.exception))

    def test_bytes_triple_exceeds_limit(self):
        msg = EmailMessage()
        big = b"x" * (MAX_ATTACHMENT_SIZE + 1)
        with self.assertRaises(ValueError):
            _attach(msg, ("big.bin", big, "application/octet-stream"))

    def test_file_path_exceeds_limit(self):
        msg = EmailMessage()
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
            f.write(b"x" * 1024)
            path = Path(f.name)
        try:
            with self.assertRaises(ValueError) as ctx:
                _attach(msg, path, max_size=512)
            self.assertIn("exceeds", str(ctx.exception))
        finally:
            path.unlink()

    def test_small_attachment_accepted(self):
        msg = EmailMessage()
        _attach(msg, ("ok.txt", b"hello"))
        parts = list(msg.iter_attachments())
        self.assertEqual(len(parts), 1)


class TestSmtpClientErrors(TestCase):
    def test_send_before_connect_raises(self):
        client = SmtpClient(host=SMTPHost("smtp.x"), user="u", password="pw")
        with self.assertRaises(RuntimeError):
            client.send(EmailMessage())
