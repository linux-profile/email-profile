import tempfile
from pathlib import Path
from unittest import TestCase

from email_profile import EmailSerializer
from email_profile.storage.dump import MessageDumper
from tests.conftest import SAMPLE_RFC822


class TestMessageDumper(TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.msg = EmailSerializer.from_raw(
            uid="1", mailbox="INBOX", raw=SAMPLE_RFC822
        )
        self.dumper = MessageDumper(self.msg)

    def tearDown(self):
        self._tmp.cleanup()

    def test_to_dict_includes_subject(self):
        self.assertEqual(self.dumper.to_dict()["subject"], "Hello")

    def test_to_json_writes_file(self):
        out = self.dumper.to_json(self.tmp)
        self.assertTrue(out.exists())
        self.assertEqual(out.suffix, ".json")

    def test_to_html_writes_file(self):
        out = self.dumper.to_html(self.tmp)
        self.assertTrue(out.exists())
        self.assertEqual(out.name, "index.html")
