# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TestCase
from src.http import urlQuote, urlQuotePlus, urlUnquote, urlUnqoutePlus

class TestQuotes(TestCase):

    def setUp(self):
        self.quoteStrings = [
            ("aa bb",           "",                 "aa%20bb"),
            ("eěe",             "",                 "e%C4%9Be"),
            ("eš/w",            "",                 "e%C5%A1%2Fw"),
            ("eš/w",            "/",                "e%C5%A1/w"),
            ("+ěščřžýáíé",      "ěščřžýáíé",        "%2Běščřžýáíé")]
        self.quotePlusStrings = [
            ("aa bb",           "",                 "aa+bb")]
        self.unquoteStrings = [
            ("aa%20bb",             "aa bb")]
        self.unquotePlusStrings = [
            ("aa+%20bb",            "aa  bb")]

    def test_urlQuote(self):
        for s, safe, qs in self.quoteStrings:
            self.assertEquals(urlQuote(s, safe), qs)

    def test_urlQuotePlus(self):
        for s, safe, qs in self.quotePlusStrings:
            self.assertEquals(urlQuotePlus(s, safe), qs)

    def test_urlUnquote(self):
        for s, us in self.unquoteStrings:
            self.assertEquals(urlUnquote(s), us)

    def test_urlUnquotePlus(self):
        for s, us in self.unquotePlusStrings:
            self.assertEquals(urlUnqoutePlus(s), us)
