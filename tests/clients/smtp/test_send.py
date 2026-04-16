from unittest import TestCase
from unittest.mock import MagicMock, patch

from email_profile import Email, EmailSerializer
from email_profile.core.types import SMTPHost
from tests.conftest import SAMPLE_RFC822, make_fake_client


def _smtp_patches(fake_smtp):
    return (
        patch(
            "email_profile.clients.smtp.client.smtplib.SMTP_SSL",
            return_value=fake_smtp,
        ),
        patch(
            "email_profile.clients.smtp.client.smtplib.SMTP",
            return_value=fake_smtp,
        ),
        patch(
            "email_profile.clients.smtp.sender.resolve_smtp_host",
            return_value=SMTPHost("smtp.test", port=465, ssl=True),
        ),
    )


class _SendTest(TestCase):
    def setUp(self):
        self.imap = make_fake_client()
        self.smtp = MagicMock()

        self._imap_patch = patch(
            "email_profile.clients.imap.client.imaplib.IMAP4_SSL",
            return_value=self.imap,
        )
        ssl_patch, plain_patch, resolve_patch = _smtp_patches(self.smtp)
        self._smtp_ssl_patch = ssl_patch
        self._smtp_plain_patch = plain_patch
        self._resolve_patch = resolve_patch

        for p in (
            self._imap_patch,
            self._smtp_ssl_patch,
            self._smtp_plain_patch,
            self._resolve_patch,
        ):
            p.start()

        self.app = Email("imap.x", "u@x.com", "pw").connect()

    def tearDown(self):
        self.app.close()
        for p in (
            self._imap_patch,
            self._smtp_ssl_patch,
            self._smtp_plain_patch,
            self._resolve_patch,
        ):
            p.stop()


class TestSend(_SendTest):
    def test_send_calls_smtp(self):
        self.app.send(to="bob@x", subject="Hi", body="hello")
        self.smtp.login.assert_called_once_with("u@x.com", "pw")
        self.smtp.send_message.assert_called_once()

    def test_send_saves_to_sent(self):
        self.app.send(to="bob@x", subject="Hi", body="hello")
        self.imap.append.assert_called_once()

    def test_send_can_skip_save_to_sent(self):
        self.app.send(
            to="bob@x", subject="Hi", body="hello", save_to_sent=False
        )
        self.imap.append.assert_not_called()

    def test_send_sets_from_when_missing(self):
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["To"] = "bob@x"
        msg["Subject"] = "t"
        msg.set_content("body")

        self.app.send_message(msg, save_to_sent=False)
        sent = self.smtp.send_message.call_args[0][0]
        self.assertEqual(sent["From"], "u@x.com")


class TestReply(_SendTest):
    def test_reply_preserves_threading(self):
        original = EmailSerializer.from_raw(
            uid="1", mailbox="INBOX", raw=SAMPLE_RFC822
        )
        original_id = original.id

        self.app.reply(original, body="thanks")

        sent = self.smtp.send_message.call_args[0][0]
        self.assertTrue(sent["Subject"].startswith("Re:"))
        self.assertEqual(sent["In-Reply-To"], original_id)
        self.assertIn(original_id, sent["References"])

    def test_reply_does_not_double_re_prefix(self):
        raw = SAMPLE_RFC822.replace(b"Subject: Hello", b"Subject: Re: hi")
        original = EmailSerializer.from_raw(uid="1", mailbox="INBOX", raw=raw)
        self.app.reply(original, body="ok", save_to_sent=False)
        sent = self.smtp.send_message.call_args[0][0]
        self.assertFalse(sent["Subject"].lower().startswith("re: re:"))


class TestForward(_SendTest):
    def test_forward_prefixes_subject(self):
        original = EmailSerializer.from_raw(
            uid="1", mailbox="INBOX", raw=SAMPLE_RFC822
        )
        self.app.forward(original, to="carol@x")
        sent = self.smtp.send_message.call_args[0][0]
        self.assertTrue(sent["Subject"].startswith("Fwd:"))

    def test_forward_quotes_original(self):
        original = EmailSerializer.from_raw(
            uid="1",
            mailbox="INBOX",
            raw=SAMPLE_RFC822,
            from_="alice@example.com",
            to_="bob@example.com",
        )
        self.app.forward(original, to="carol@x", body="please see below")
        sent = self.smtp.send_message.call_args[0][0]
        text = ""
        for part in sent.walk():
            if part.get_content_type() == "text/plain":
                text = part.get_content()
                break
        self.assertIn("Forwarded message", text)
        self.assertIn("alice@example.com", text)
