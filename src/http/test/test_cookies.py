from __future__ import unicode_literals
from unittest import TestCase
from src.http.cookies import Cookie
import datetime


class TestCookie(TestCase):

    def setUp(self):
        self.cookieInputString1 = "sessionid=\"7d49f02725144e; 850aaf9f59f7af4f7a\"; Domain=.circuitlab.com; expires=Wed, 24-Apr-2013 04:35:50 GMT; httponly; Max-Age=2592000; Path=/; secure"

    def test_initCookieString1(self):
        cookie = Cookie(self.cookieInputString1)
        self.assertEquals(cookie.name, "sessionid")
        self.assertEquals(cookie.value, "7d49f02725144e; 850aaf9f59f7af4f7a")
        self.assertEquals(cookie.domain, ".circuitlab.com")
        self.assertEqual(cookie.expires, datetime.datetime(2013, 4, 24, 4, 35, 50))
