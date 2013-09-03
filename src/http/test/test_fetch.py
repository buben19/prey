from __future__ import unicode_literals
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from src.address import Address
from src.http.cookies import Cookie
from src.http.headers import Header
from src.http.fetch import PageFetchConfig, PageFetcher
from src.http.page import HTTPPage, PageTools, SUCCESS, REDIRECT, NOT_FOUND
from src.url import Url
from twisted.trial.unittest import TestCase
import threading

class TestFetchConfig(TestCase):

    def test_configDefaults(self):
        u = Url("http://example.com/path")
        config = PageFetchConfig(u)
        self.assertEquals(config.url, u)
        self.assertEquals(config.method, "GET")
        self.assertIsNone(config.postData)
        self.assertIsInstance(config.headers, list)
        self.assertEquals(config.headers, [])
        self.assertIsNone(config.agent)
        self.assertEquals(config.timeout, 0)
        self.assertIsInstance(config.cookies, list)
        self.assertEquals(config.cookies, [])

    def test_configPopulated(self):
        u = Url("http://example.com/path")
        headers = [
            Header("name", "value")]
        cookies = [
            Cookie.buildCookie("cookie1", "value1"),
            Cookie.buildCookie("cookie2", "value2"),
            Cookie.buildCookie("cookie3", "value3")]
        config = PageFetchConfig(
            u,
            method          = "POST",
            postData        = "my string",
            headers         = headers,
            agent           = "my agent",
            timeout         = 1,
            cookies         = cookies)
        self.assertEquals(config.url, u)
        self.assertEquals(config.method, "POST")
        self.assertEquals(config.postData, "my string")
        self.assertEquals(config.headers, headers)
        self.assertEquals(config.agent, "my agent")
        self.assertEquals(config.timeout, 1)
        self.assertEquals(config.cookies, cookies)

class TestPageFetcher(TestCase):

    serverThread = None

    def setUp(self):
        self.startServer()
        self.baseUrl = Url("http://127.0.0.1:8000/")
        self.fetchAddress = Address(self.baseUrl.host)
        self.fetchPort = self.baseUrl.port

    def startServer(self):
        if self.serverThread is None or not self.serverThread.isAlive():
            serverAddress = ('', 8000)
            httpd = HTTPServer(
                serverAddress,
                ResquestHandlerTestClass)
            self.serverThread = threading.Thread(
                target = httpd.handle_request)
            self.serverThread.daemon = True
            self.serverThread.start()

    def _basicPageTests(self, page):
        self.assertIsInstance(page, HTTPPage)
        self.assertIsInstance(page.version, unicode)
        self.assertIsInstance(page.status, unicode)
        self.assertIsInstance(page.message, unicode)
        self.assertIsInstance(page.headers, list)

    def _testPageContent(self, page):
        self.assertIsInstance(page.byteContent, str)
        self.assertIsInstance(page.decodedContent, unicode)
        self.assertEquals(page.byteContent, b"my response header")
        self.assertEquals(page.byteContent, "my response header")

    def _testPageNoContent(self, page):
        self.assertIsNone(page.byteContent)
        self.assertIsNone(page.decodedContent)

    def test_fetchSuccess(self):
        def page(page):
            self._basicPageTests(page)
            self._testPageContent(page)
            self.assertEquals(page.pageInfo, SUCCESS)
        url = Url.join(self.baseUrl, "/success")
        config = PageFetchConfig(url)
        d = PageFetcher(config, self.fetchAddress, self.fetchPort).getPage()
        d.addCallback(page)
        return d

    def test_fetchRedirect(self):
        def page(page):
            self._basicPageTests(page)
            self._testPageNoContent(page)
            redirectUrl = Url("http://localhost/another/path")
            self.assertEquals(PageTools.getLocation(page.headers), redirectUrl)
            self.assertEquals(page.pageInfo, REDIRECT)
        url = Url.join(self.baseUrl, "/redirect")
        config = PageFetchConfig(url)
        d = PageFetcher(config, self.fetchAddress, self.fetchPort).getPage()
        d.addCallback(page)
        return d

    def test_fetchPageRedirectWithNoLocation(self):
        def page(page):
            self._basicPageTests(page)
            self._testPageContent(page)
            self.assertIsNone(PageTools.getLocation(page.headers))
            self.assertEquals(page.pageInfo, REDIRECT)
        url = Url.join(self.baseUrl, "/redirect/with/no/location")
        config = PageFetchConfig(url)
        d = PageFetcher(config, self.fetchAddress, self.fetchPort).getPage()
        d.addCallback(page)
        return d

    def test_fetchNotFound(self):
        def page(page):
            self._basicPageTests(page)
            self._testPageContent(page)
            self.assertEquals(page.pageInfo, NOT_FOUND)
        url = Url.join(self.baseUrl, "/not/found")
        config = PageFetchConfig(url)
        d = PageFetcher(config, self.fetchAddress, self.fetchPort).getPage()
        d.addCallback(page)
        return d

class ResquestHandlerTestClass(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/success":
            self.sendSuccess()
        if self.path == "/redirect":
            self.sendRedirect()
        if self.path == "/redirect/with/no/location":
            self.sendRedirectWithNoLocation()
        if self.path == "/not/found":
            self.sendNotFound()

    def getResponseContent(self):
        return b"my response header"

    def getResponseHeaders(self):
        return [
            ("Name",                "value"),
            ("Content-Type",        "text/html; charset=UTF-8")]

    def sendSuccess(self):
        self.send_response(200)
        self.sendHeaders()
        self.end_headers()
        self.sendContent()

    def sendRedirect(self):
        self.send_response(301)
        self.sendHeaders()
        self.send_header("Location", "http://localhost/another/path")
        self.end_headers()
        self.sendContent()

    def sendRedirectWithNoLocation(self):
        self.send_response(301)
        self.sendHeaders()
        self.end_headers()
        self.sendContent()

    def sendNotFound(self):
        self.send_response(404)
        self.sendHeaders()
        self.end_headers()
        self.sendContent()

    def sendHeaders(self):
        for key, value in self.getResponseHeaders():
            self.send_header(key, value)

    def sendContent(self):
        self.wfile.write(self.getResponseContent())

    def log_message(self, format, *args):
        return
