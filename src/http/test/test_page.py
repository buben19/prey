from __future__ import unicode_literals
from src.http.page import PageTools
from src.http.headers import Header
from unittest import TestCase


class TestPageTools(TestCase):

    def test_utf8(self):
        headers = [Header('Content-Type', 'text/html; charset=utf-8')]
        self.assertEquals("utf-8", PageTools.getCharset(headers))

    def test_charsetMissing1(self):
        headers = [Header('Content-Type', 'text/html; charset=')]
        self.assertIsNone(PageTools.getCharset(headers))

    def test_charsetMissing2(self):
        headers = [Header('Content-Type', 'text/html; charset')]
        self.assertIsNone(PageTools.getCharset(headers))

    def test_unsupportedCharset(self):
        headers = [Header('Content-Type', 'text/html; charset=utf-junk')]
        self.assertIsNone(PageTools.getCharset(headers))
