from sharethis import __version__
from unittest import TestCase


class TestGlobal(TestCase):
    def test_version(self):
        self.assertEqual(__version__, '0.1.0')
