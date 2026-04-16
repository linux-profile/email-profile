from unittest import TestCase
from unittest.mock import patch

from email_profile import Email, NotConnected
from tests.conftest import GMAIL_LIST, make_fake_client


class TestConnection(TestCase):
    def test_does_not_connect_eagerly(self):
        fake = make_fake_client()
        with patch(
            "email_profile.imap_session.imaplib.IMAP4_SSL", return_value=fake
        ):
            Email("imap.x", "u", "p")
        fake.login.assert_not_called()

    def test_mailbox_requires_connection(self):
        fake = make_fake_client()
        with patch(
            "email_profile.imap_session.imaplib.IMAP4_SSL", return_value=fake
        ):
            app = Email("imap.x", "u", "p")
        with self.assertRaises(NotConnected):
            app.mailbox("INBOX")

    def test_context_manager_logs_in_and_out(self):
        fake = make_fake_client()
        with (
            patch(
                "email_profile.imap_session.imaplib.IMAP4_SSL",
                return_value=fake,
            ),
            Email("imap.x", "u", "p") as app,
        ):
            self.assertIn("INBOX", app.mailboxes())
        fake.login.assert_called_once()
        fake.logout.assert_called_once()

    def test_unknown_mailbox_raises(self):
        fake = make_fake_client()
        with (
            patch(
                "email_profile.imap_session.imaplib.IMAP4_SSL",
                return_value=fake,
            ),
            Email("imap.x", "u", "p") as app,
            self.assertRaises(KeyError),
        ):
            app.mailbox("Trash")


class TestProviderFactories(TestCase):
    def test_gmail(self):
        self.assertEqual(Email.gmail("u", "p").server, "imap.gmail.com")

    def test_outlook(self):
        self.assertEqual(
            Email.outlook("u", "p").server, "outlook.office365.com"
        )

    def test_icloud(self):
        self.assertEqual(Email.icloud("u", "p").server, "imap.mail.me.com")

    def test_yahoo(self):
        self.assertEqual(Email.yahoo("u", "p").server, "imap.mail.yahoo.com")

    def test_hostinger(self):
        self.assertEqual(
            Email.hostinger("u", "p").server, "imap.hostinger.com"
        )

    def test_zoho(self):
        self.assertEqual(Email.zoho("u", "p").server, "imap.zoho.com")

    def test_fastmail(self):
        self.assertEqual(Email.fastmail("u", "p").server, "imap.fastmail.com")


class TestFromEmail(TestCase):
    def test_uses_resolver(self):
        from email_profile import IMAPHost

        with patch(
            "email_profile.credentials.resolve_imap_host",
            return_value=IMAPHost("imap.test", port=993),
        ):
            app = Email.from_email("a@test.example", "pw")
        self.assertEqual(app.server, "imap.test")
        self.assertEqual(app.user, "a@test.example")


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
        self.assertEqual(app.server, "imap.x.com")

    def test_auto_discovers_when_server_missing(self):
        with patch.dict(
            "os.environ",
            {"EMAIL_USERNAME": "a@gmail.com", "EMAIL_PASSWORD": "pw"},
            clear=True,
        ):
            app = Email.from_env(load_dotenv=False)
        self.assertEqual(app.server, "imap.gmail.com")

    def test_missing_credentials_raises(self):
        with (
            patch.dict("os.environ", {}, clear=True),
            self.assertRaises(KeyError),
        ):
            Email.from_env(load_dotenv=False)


class TestMailboxProperties(TestCase):
    def setUp(self):
        self.fake = make_fake_client(mailboxes=GMAIL_LIST)
        self._patcher = patch(
            "email_profile.imap_session.imaplib.IMAP4_SSL",
            return_value=self.fake,
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
            "email_profile.imap_session.imaplib.IMAP4_SSL",
            return_value=self.fake,
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


class TestPublicProperties(TestCase):
    def test_properties_expose_config(self):
        app = Email("imap.x.com", "u", "pw", port=143, ssl=False)
        self.assertEqual(app.server, "imap.x.com")
        self.assertEqual(app.user, "u")
        self.assertEqual(app.port, 143)
        self.assertFalse(app.ssl)

    def test_is_connected_false_before_connect(self):
        app = Email("imap.x.com", "u", "pw")
        self.assertFalse(app.is_connected)

    def test_is_connected_true_after_connect(self):
        fake = make_fake_client()
        with (
            patch(
                "email_profile.imap_session.imaplib.IMAP4_SSL",
                return_value=fake,
            ),
            Email("imap.x", "u", "p") as app,
        ):
            self.assertTrue(app.is_connected)
        self.assertFalse(app.is_connected)


class TestConstructorOverloads(TestCase):
    def test_three_positional_args_explicit(self):
        app = Email("imap.x.com", "u", "pw")
        self.assertEqual(app.server, "imap.x.com")

    def test_keyword_form(self):
        app = Email(server="imap.x.com", user="u", password="pw")
        self.assertEqual(app.server, "imap.x.com")

    def test_two_args_with_email_auto_discovers(self):
        from email_profile import IMAPHost

        with patch(
            "email_profile.credentials.resolve_imap_host",
            return_value=IMAPHost("imap.test"),
        ):
            app = Email("u@test.example", "pw")
        self.assertEqual(app.server, "imap.test")
        self.assertEqual(app.user, "u@test.example")

    def test_zero_args_reads_env(self):
        with (
            patch.dict(
                "os.environ",
                {
                    "EMAIL_SERVER": "imap.x.com",
                    "EMAIL_USERNAME": "u@x.com",
                    "EMAIL_PASSWORD": "pw",
                },
                clear=True,
            ),
            patch("email_profile.email.EmailFactories.from_env") as build,
        ):
            from email_profile.credentials import Credentials

            build.return_value = Credentials(
                server="imap.x.com", user="u@x.com", password="pw"
            )
            app = Email()
        self.assertEqual(app.server, "imap.x.com")

    def test_zero_args_without_env_raises(self):
        with (
            patch(
                "email_profile.email.EmailFactories.from_env",
                side_effect=KeyError("nope"),
            ),
            self.assertRaises(KeyError),
        ):
            Email()

    def test_partial_args_raises(self):
        with self.assertRaises(TypeError):
            Email("imap.x.com")


class TestNoop(TestCase):
    def test_noop_calls_imap_noop(self):
        fake = make_fake_client()
        with (
            patch(
                "email_profile.imap_session.imaplib.IMAP4_SSL",
                return_value=fake,
            ),
            Email("imap.x", "u", "p") as app,
        ):
            app.noop()
        fake.noop.assert_called_once()


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
                    EmailSerializer.from_raw(uid=uid, mailbox="INBOX", raw=raw)
                )

            fake = make_fake_client()
            with (
                patch(
                    "email_profile.imap_session.imaplib.IMAP4_SSL",
                    return_value=fake,
                ),
                Email("imap.x", "u", "p") as app,
            ):
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
            with (
                patch(
                    "email_profile.imap_session.imaplib.IMAP4_SSL",
                    return_value=fake,
                ),
                Email("imap.x", "u", "p") as app,
                self.assertRaises(KeyError),
            ):
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
            with (
                patch(
                    "email_profile.imap_session.imaplib.IMAP4_SSL",
                    return_value=fake,
                ),
                Email("imap.x", "u", "p") as app,
            ):
                n = app.restore_eml(tmp)

            self.assertEqual(n, 2)
            self.assertEqual(fake.append.call_count, 2)
