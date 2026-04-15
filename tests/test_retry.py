from unittest import TestCase
from unittest.mock import patch

from email_profile import QuotaExceeded, RateLimited, with_retry


class TestWithRetry(TestCase):
    def test_succeeds_first_try(self):
        calls = {"n": 0}

        @with_retry(attempts=3, initial_delay=0)
        def op():
            calls["n"] += 1
            return "ok"

        self.assertEqual(op(), "ok")
        self.assertEqual(calls["n"], 1)

    def test_retries_transient_error(self):
        calls = {"n": 0}

        @with_retry(attempts=3, initial_delay=0)
        def op():
            calls["n"] += 1
            if calls["n"] < 3:
                raise OSError("flaky")
            return "ok"

        with patch("email_profile.retry.time.sleep"):
            self.assertEqual(op(), "ok")
        self.assertEqual(calls["n"], 3)

    def test_gives_up_after_attempts(self):
        @with_retry(attempts=2, initial_delay=0)
        def op():
            raise OSError("boom")

        with (
            patch("email_profile.retry.time.sleep"),
            self.assertRaises(OSError),
        ):
            op()

    def test_quota_is_not_retried(self):
        calls = {"n": 0}

        @with_retry(attempts=5, initial_delay=0)
        def op():
            calls["n"] += 1
            raise QuotaExceeded("over quota")

        with self.assertRaises(QuotaExceeded):
            op()
        self.assertEqual(calls["n"], 1)

    def test_rate_limited_waits_longer(self):
        calls = {"n": 0}

        @with_retry(attempts=3, initial_delay=0.1)
        def op():
            calls["n"] += 1
            if calls["n"] < 3:
                raise RateLimited("slow down")
            return "ok"

        with patch("email_profile.retry.time.sleep") as sleep:
            op()
        # Two sleeps, both with the rate-limited multiplier (initial * 4).
        self.assertEqual(sleep.call_count, 2)
