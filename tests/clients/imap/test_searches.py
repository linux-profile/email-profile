from unittest import TestCase
from unittest.mock import patch

from email_profile import Email
from tests.conftest import make_fake_client


class TestWhereLazy(TestCase):
    def setUp(self):
        self.fake = make_fake_client()
        self._patcher = patch(
            "email_profile.clients.imap.client.imaplib.IMAP4_SSL",
            return_value=self.fake,
        )
        self._patcher.start()
        self.app = Email("imap.x", "u", "p").connect()

    def tearDown(self):
        self.app.close()
        self._patcher.stop()

    def test_count_does_not_fetch_bodies(self):
        n = self.app.inbox.where().count()
        self.assertEqual(n, 2)
        fetch_calls = [
            c for c in self.fake.uid.call_args_list if c.args[0] == "fetch"
        ]
        self.assertEqual(fetch_calls, [])

    def test_exists_short_circuits(self):
        self.assertTrue(self.app.inbox.where().exists())

    def test_uids(self):
        self.assertEqual(self.app.inbox.where().uids(), ["1", "2"])

    def test_messages_yields(self):
        messages = list(self.app.inbox.where().messages())
        self.assertEqual(len(messages), 1)

    def test_independent_state_between_queries(self):
        first = list(self.app.inbox.where().messages())
        second = list(self.app.inbox.where().messages())
        self.assertIsNot(first, second)


class TestFetchModes(TestCase):
    def setUp(self):
        self.fake = make_fake_client()
        self._patcher = patch(
            "email_profile.clients.imap.client.imaplib.IMAP4_SSL",
            return_value=self.fake,
        )
        self._patcher.start()
        self.app = Email("imap.x", "u", "p").connect()

    def tearDown(self):
        self.app.close()
        self._patcher.stop()

    def _last_fetch_spec(self):
        for call in reversed(self.fake.uid.call_args_list):
            if call.args[0] == "fetch":
                return call.args[2]
        return None

    def test_default_mode_is_full(self):
        list(self.app.inbox.where().messages())
        self.assertEqual(self._last_fetch_spec(), "(RFC822)")

    def test_text_mode_uses_peek(self):
        list(self.app.inbox.where().messages(mode="text"))
        self.assertIn("BODY.PEEK[TEXT]", self._last_fetch_spec())

    def test_headers_mode_skips_body(self):
        list(self.app.inbox.where().messages(mode="headers"))
        spec = self._last_fetch_spec()
        self.assertIn("BODY.PEEK[HEADER]", spec)
        self.assertNotIn("BODY.PEEK[TEXT]", spec)

    def test_invalid_mode_raises(self):
        with self.assertRaises(ValueError):
            list(self.app.inbox.where().messages(mode="banana"))


class TestChunkAndProgress(TestCase):
    def setUp(self):
        self.fake = make_fake_client()
        self._patcher = patch(
            "email_profile.clients.imap.client.imaplib.IMAP4_SSL",
            return_value=self.fake,
        )
        self._patcher.start()
        self.app = Email("imap.x", "u", "p").connect()

    def tearDown(self):
        self.app.close()
        self._patcher.stop()

    def test_chunk_size_passes_to_fetch(self):
        list(self.app.inbox.where().messages(chunk_size=1))
        # 2 UIDs, chunk_size=1 → 2 fetch calls.
        fetch_calls = [
            c for c in self.fake.uid.call_args_list if c.args[0] == "fetch"
        ]
        self.assertEqual(len(fetch_calls), 2)

    def test_on_progress_is_called(self):
        seen: list[tuple[int, int]] = []
        list(
            self.app.inbox.where().messages(
                chunk_size=1, on_progress=lambda d, t: seen.append((d, t))
            )
        )
        self.assertEqual(seen, [(1, 2), (2, 2)])


class TestUidsCache(TestCase):
    def setUp(self):
        self.fake = make_fake_client()
        self._patcher = patch(
            "email_profile.clients.imap.client.imaplib.IMAP4_SSL",
            return_value=self.fake,
        )
        self._patcher.start()
        self.app = Email("imap.x", "u", "p").connect()

    def tearDown(self):
        self.app.close()
        self._patcher.stop()

    def _search_calls(self):
        return [
            c for c in self.fake.uid.call_args_list if c.args[0] == "search"
        ]

    def test_repeated_count_only_searches_once(self):
        w = self.app.inbox.where()
        w.count()
        w.count()
        w.exists()
        self.assertEqual(len(self._search_calls()), 1)

    def test_clear_cache_invalidates_cache(self):
        w = self.app.inbox.where()
        w.count()
        w.clear_cache().count()
        self.assertEqual(len(self._search_calls()), 2)
