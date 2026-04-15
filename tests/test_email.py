from unittest import TestCase
from unittest.mock import patch

from email_profile import Email, NotConnected
from tests.conftest import GMAIL_LIST, make_fake_client


class TestConnection(TestCase):

    def test_does_not_connect_eagerly(self):
        fake = make_fake_client()
        with patch(
            "email_profile.email.imaplib.IMAP4_SSL", return_value=fake
        ):
            Email("imap.x", "u", "p")
        fake.login.assert_not_called()

    def test_mailbox_requires_connection(self):
        fake = make_fake_client()
        with patch(
            "email_profile.email.imaplib.IMAP4_SSL", return_value=fake
        ):
            app = Email("imap.x", "u", "p")
        with self.assertRaises(NotConnected):
            app.mailbox("INBOX")

    def test_context_manager_logs_in_and_out(self):
        fake = make_fake_client()
        with patch(
            "email_profile.email.imaplib.IMAP4_SSL", return_value=fake
        ), Email("imap.x", "u", "p") as app:
            self.assertIn("INBOX", app.mailboxes())
        fake.login.assert_called_once()
        fake.logout.assert_called_once()

    def test_unknown_mailbox_raises(self):
        fake = make_fake_client()
        with patch(
            "email_profile.email.imaplib.IMAP4_SSL", return_value=fake
        ), Email("imap.x", "u", "p") as app, self.assertRaises(KeyError):
            app.mailbox("Trash")


class TestProviderFactories(TestCase):

    def test_gmail(self):
        self.assertEqual(Email.gmail("u", "p")._server, "imap.gmail.com")

    def test_outlook(self):
        self.assertEqual(
            Email.outlook("u", "p")._server, "outlook.office365.com"
        )

    def test_icloud(self):
        self.assertEqual(
            Email.icloud("u", "p")._server, "imap.mail.me.com"
        )

    def test_yahoo(self):
        self.assertEqual(
            Email.yahoo("u", "p")._server, "imap.mail.yahoo.com"
        )

    def test_hostinger(self):
        self.assertEqual(
            Email.hostinger("u", "p")._server, "imap.hostinger.com"
        )

    def test_zoho(self):
        self.assertEqual(Email.zoho("u", "p")._server, "imap.zoho.com")

    def test_fastmail(self):
        self.assertEqual(
            Email.fastmail("u", "p")._server, "imap.fastmail.com"
        )


class TestFromEmail(TestCase):

    def test_uses_resolver(self):
        from email_profile import IMAPHost

        with patch(
            "email_profile.email.resolve_imap_host",
            return_value=IMAPHost("imap.test", port=993),
        ):
            app = Email.from_email("a@test.example", "pw")
        self.assertEqual(app._server, "imap.test")
        self.assertEqual(app._user, "a@test.example")


class TestFromEnv(TestCase):

    def test_uses_explicit_server(self):
        with patch.dict(
            "os.environ",
            {
                "EMAIL_SERVER": "imap.x.com",
                "EMAIL_USERNAME": "u@x.com",
                "EMAIL_PASSWORD": "pw",
            },
            clear=True,
        ):
            app = Email.from_env(load_dotenv=False)
        self.assertEqual(app._server, "imap.x.com")

    def test_auto_discovers_when_server_missing(self):
        with patch.dict(
            "os.environ",
            {"EMAIL_USERNAME": "a@gmail.com", "EMAIL_PASSWORD": "pw"},
            clear=True,
        ):
            app = Email.from_env(load_dotenv=False)
        self.assertEqual(app._server, "imap.gmail.com")

    def test_missing_credentials_raises(self):
        with patch.dict("os.environ", {}, clear=True), self.assertRaises(
            KeyError
        ):
            Email.from_env(load_dotenv=False)


class TestMailboxProperties(TestCase):

    def setUp(self):
        self.fake = make_fake_client(mailboxes=GMAIL_LIST)
        self._patcher = patch(
            "email_profile.email.imaplib.IMAP4_SSL", return_value=self.fake
        )
        self._patcher.start()
        self.app = Email("imap.x", "u", "p").connect()

    def tearDown(self):
        self.app.close()
        self._patcher.stop()

    def test_inbox(self):
        self.assertEqual(self.app.inbox.name, "INBOX")

    def test_sent(self):
        self.assertIn("Sent", self.app.sent.name)

    def test_spam(self):
        self.assertIn("Spam", self.app.spam.name)

    def test_trash(self):
        self.assertIn("Trash", self.app.trash.name)

    def test_drafts(self):
        self.assertIn("Drafts", self.app.drafts.name)


class TestQueryShortcuts(TestCase):

    def setUp(self):
        self.fake = make_fake_client()
        self._patcher = patch(
            "email_profile.email.imaplib.IMAP4_SSL", return_value=self.fake
        )
        self._patcher.start()
        self.app = Email("imap.x", "u", "p").connect()

    def tearDown(self):
        self.app.close()
        self._patcher.stop()

    def test_unread_uses_unseen_clause(self):
        self.app.unread().count()
        searches = [
            c for c in self.fake.uid.call_args_list if c.args[0] == "search"
        ]
        self.assertTrue(any("(UNSEEN)" in str(c) for c in searches))

    def test_recent_uses_since_clause(self):
        self.app.recent(days=3).count()
        searches = [
            c for c in self.fake.uid.call_args_list if c.args[0] == "search"
        ]
        self.assertTrue(any("SINCE" in str(c) for c in searches))

    def test_search_uses_text_clause(self):
        self.app.search("invoice").count()
        searches = [
            c for c in self.fake.uid.call_args_list if c.args[0] == "search"
        ]
        self.assertTrue(any("TEXT" in str(c) for c in searches))


class TestRestore(TestCase):

    def test_restore_re_uploads(self):
        import tempfile
        from pathlib import Path

        from email_profile import EmailSerializer, Storage

        with tempfile.TemporaryDirectory() as tmp:
            storage = Storage(Path(tmp) / "src.db")
            for uid in ("1", "2"):
                from tests.conftest import SAMPLE_RFC822

                raw = SAMPLE_RFC822.replace(
                    b"<abc@example.com>", f"<{uid}@x>".encode()
                )
                storage.save(
                    EmailSerializer.from_raw(
                        uid=uid, mailbox="INBOX", raw=raw
                    )
                )

            fake = make_fake_client()
            with patch(
                "email_profile.email.imaplib.IMAP4_SSL", return_value=fake
            ), Email("imap.x", "u", "p") as app:
                n = app.restore(storage)

            self.assertEqual(n, 2)
            self.assertEqual(fake.append.call_count, 2)
            storage.dispose()

    def test_restore_unknown_mailbox_raises(self):
        import tempfile
        from pathlib import Path

        from email_profile import EmailSerializer, Storage

        with tempfile.TemporaryDirectory() as tmp:
            storage = Storage(Path(tmp) / "src.db")
            storage.save(
                EmailSerializer.from_raw(
                    uid="1", mailbox="Archive", raw=b"From: a\r\n\r\nx"
                )
            )

            fake = make_fake_client()
            with patch(
                "email_profile.email.imaplib.IMAP4_SSL", return_value=fake
            ), Email("imap.x", "u", "p") as app, self.assertRaises(KeyError):
                app.restore(storage)

            storage.dispose()

    def test_restore_eml_from_directory(self):
        import tempfile
        from pathlib import Path

        from email_profile import Email
        from tests.conftest import SAMPLE_RFC822

        with tempfile.TemporaryDirectory() as tmp:
            box = Path(tmp) / "INBOX"
            box.mkdir()
            (box / "1.eml").write_bytes(SAMPLE_RFC822)
            (box / "2.eml").write_bytes(SAMPLE_RFC822)

            fake = make_fake_client()
            with patch(
                "email_profile.email.imaplib.IMAP4_SSL", return_value=fake
            ), Email("imap.x", "u", "p") as app:
                n = app.restore_eml(tmp)

            self.assertEqual(n, 2)
            self.assertEqual(fake.append.call_count, 2)
