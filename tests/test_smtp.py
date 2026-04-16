from email.message import EmailMessage
from unittest import TestCase
from unittest.mock import MagicMock, patch

from email_profile import SmtpClient
from email_profile.smtp_client import _build_message
from email_profile.types import SMTPHost


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
            "email_profile.smtp_client.smtplib.SMTP_SSL",
            return_value=self.fake,
        )
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_connect_logs_in(self):
        SmtpClient(self.host, "u", "pw").connect()
        self.fake.login.assert_called_once_with("u", "pw")

    def test_context_manager_quits(self):
        with SmtpClient(self.host, "u", "pw") as client:
            self.assertTrue(client.is_connected)
        self.fake.quit.assert_called_once()

    def test_send_delegates_to_send_message(self):
        msg = EmailMessage()
        with SmtpClient(self.host, "u", "pw") as client:
            client.send(msg)
        self.fake.send_message.assert_called_once_with(msg)


class TestSmtpClientStartTLS(TestCase):
    def test_starttls_upgrades(self):
        host = SMTPHost("smtp.x", port=587, ssl=False, starttls=True)
        fake = MagicMock()
        with patch(
            "email_profile.smtp_client.smtplib.SMTP", return_value=fake
        ):
            SmtpClient(host, "u", "pw").connect()
        fake.starttls.assert_called_once()
        fake.login.assert_called_once_with("u", "pw")


class TestSmtpClientErrors(TestCase):
    def test_send_before_connect_raises(self):
        client = SmtpClient(SMTPHost("smtp.x"), "u", "pw")
        with self.assertRaises(RuntimeError):
            client.send(EmailMessage())
