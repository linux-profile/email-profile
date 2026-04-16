from unittest import TestCase

from email_profile.storage.db import Base, make_session


class TestMakeSession(TestCase):
    def test_returns_engine_and_factory(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            url = f"sqlite:///{tmp}/x.db"
            engine, factory = make_session(url)
            self.assertEqual(engine.url.render_as_string(), url)
            with factory() as session:
                self.assertTrue(session.is_active)


class TestBase(TestCase):
    def test_is_declarative(self):
        self.assertTrue(hasattr(Base, "metadata"))
