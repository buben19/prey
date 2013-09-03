# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import urllib
import src.http as http
import string
import itertools
from src.tools import omdict
from src.python.orderedmultidict1d import omdict1D
from src.url import Path, Query, Url


class TestPath(unittest.TestCase):

    def setUp(self):

        # set of characters which must be quoted
        self.quotedCharsSet = set(string.printable)
        self.quotedCharsSet -= (set(string.ascii_letters) |
                                set(string.digits) |
                                set(Path.SAFE_SEGMENT_CHARS))

        # list of possible string to parse and their propre results
        self.testParseStrings = [
            ("",                        []),
            ("/",                       []),
            ("///",                     []),
            ("index.html",              ["index.html"]),
            ("/index.html",             ["index.html"]),
            ("/foo/bar",                ["foo", "bar"]),
            ("foo/bar",                 ["foo", "bar"]),
            ("path%20to",               ["path to"]),
            ("path to",                 ["path to"]),
            ("foo%",                    ["foo%"]),
            (Path.SAFE_SEGMENT_CHARS,   [Path.SAFE_SEGMENT_CHARS]),
            ("/path/to/dir/",           ["path", "to", "dir", ""]),
            ("/path/somě/unícódé",      ["path", "somě", "unícódé"])]

        # list of initialization iterables
        self.testInitIterables = [
            ["path", "to", "resource"],
            ["path%20to"],
            ["path "]]

    def _initPath(self):
        result = []
        for i, j in self.testParseStrings:
            result.append((i, j))
        for i in self.testInitIterables:
            result.append((i, i))
        for init, segments in result:
            yield Path(init), segments

    def _stringFromSegments(self, segments):
        def encode(segment):
            return urllib.quote(segment.encode("utf-8"),
                    Path.SAFE_SEGMENT_CHARS.encode("utf-8")).decode("utf-8")
        return "/" + "/".join(map(encode, segments))

    def test_parse(self):
        for parseString, result in self.testParseStrings:
            self.assertEquals(result, Path.parse(parseString))

    def test_init(self):
        for path, segments in self._initPath():
            self.assertEquals(unicode(path), self._stringFromSegments(segments))

    def test_segmentsGetter(self):
        for path, segments in self._initPath():
            self.assertEquals(path.segments, segments)

    def test_segmentSetterList(self):
        newSegments = ["one", "two", "three"]
        for path, segments in self._initPath():
            self.assertEquals(segments, path.segments)
            path.segments = newSegments
            self.assertEquals(newSegments, path.segments)

    def test_segmentSetterString(self):
        for path, segments in self._initPath():
            for string, resultSegments in self.testParseStrings:
                path.segments = string
                self.assertEquals(str(path), self._stringFromSegments(resultSegments))
                self.assertEquals(path.segments, resultSegments)

    def test_segmentSetterNotList(self):
        newSegments = object()
        for path, segments in self._initPath():
            self.assertEquals(path.segments, segments)
            oldLen = len(path.segments)
            self.assertRaises(TypeError, path.__setattr__, 'segments', newSegments)
            self.assertEquals(path.segments, segments)
            self.assertEquals(len(path.segments), oldLen)

    def test_segmentSetterNotContainsString(self):
        newSegments = ["one", "two", "three", object()]
        for path, segments in self._initPath():
            oldLen = len(path.segments)
            self.assertRaises(TypeError, path.__setattr__, 'segments', newSegments)
            self.assertEquals(path.segments, segments)
            self.assertEquals(len(path.segments), oldLen)

    def test_loadIterable(self):
        for iterable in self.testInitIterables:
            path = Path("/")
            self.assertEquals(0, len(path.segments))
            self.assertEquals(path, path.load(iterable))
            self.assertEquals(path.segments, iterable)

    def test_loadString(self):
        for init, segments in self.testParseStrings:
            path = Path("/")
            self.assertEquals(0, len(path.segments))
            self.assertEquals(path, path.load(init))
            self.assertEquals(path.segments, segments)

    def test_loadNotList(self):
        for path, segments in self._initPath():
            self.assertRaises(TypeError, path.load, True)
            self.assertEquals(path.segments, segments)

    def test_addIterable(self):
        for iterable in self.testInitIterables:
            path = Path(iterable)
            self.assertEquals(path.segments, iterable)
            self.assertEquals(path.add(iterable), path)
            self.assertEquals(path.segments, iterable * 2)

    def test_addString(self):
        for init, segments in self.testParseStrings:
            path = Path(init)
            self.assertEquals(path.segments, segments)
            self.assertEquals(path.add(init), path)
            self.assertEquals(path.segments, segments * 2)

    def test_addWrongType(self):
        path = Path("/")
        self.assertRaises(TypeError, path.add, object)
        self.assertEquals(path.segments, [])

    def test_addIterableWithNoString(self):
        iterable = ["one", "two", "three", object()]
        path = Path("/")
        self.assertRaises(TypeError, path.add, iterable)
        self.assertEquals(path.segments, [])

    def test_clear(self):
        for path, segments in  self._initPath():
            self.assertEquals(path.clear(), path)
            self.assertEquals(path.segments, [])

    def test_repr(self):
        for path, segments in self._initPath():
            self.assertEquals(repr(path), "<%s ('%s')>" % (path.__class__.__name__, self._stringFromSegments(segments)))

    def test_str(self):
        for path, segments in self._initPath():
            self.assertEquals(str(path), self._stringFromSegments(segments))

    def test_nonzero(self):
        for path, segments in self._initPath():
            self.assertEquals(bool(segments), path.__nonzero__())

    def test_eq(self):
        for init, segments in self.testParseStrings:
            path1 = Path(init)
            path2 = Path(init)
            path1.add("new")
            path2.add(["new"])
            self.assertEquals(path1, path2)

    def test_eqNotPath(self):
        self.assertEquals(NotImplemented, Path("/").__eq__(object()))

    def test_ne(self):
        for init, segments in self.testParseStrings:
            path1 = Path(init)
            path2 = Path(init)
            path2.add("new")
            self.assertNotEquals(path1, path2)

    def test_neNotPath(self):
        self.assertEquals(NotImplemented, Path("/").__eq__(object()))

    def test_neCase(self):
        for init, segments in self.testParseStrings:
            path1 = Path(init)
            path2 = Path(init)
            path1.add("new")
            path2.add(["NEW"])
            self.assertNotEquals(path1, path2)

class TestQuery(unittest.TestCase):

    def setUp(self):
        quotedCharsSet = set(string.printable)
        self.quotedNameCharsSet = quotedCharsSet - \
            (set(string.ascii_letters) |
            set(string.digits) |
            set(Query.SAFE_NAME_CHARS))
        self.quotedValueCharsSet = quotedCharsSet - \
            (set(string.ascii_letters) |
            set(string.digits) |
            set(Query.SAFE_NAME_CHARS))

        quotedNameCharsStr = "".join(self.quotedNameCharsSet)
        quotedValueCharsStr = "".join(self.quotedValueCharsSet)

        self.testParseStrings = [
            ("one=1&two=2&one=3",               [('one', '1'), ('two', '2'), ('one', '3')]),
            ("",                                []),
            ("one+two=12&two=2",                [('one two', '12'), ('two', '2')]),
            ("one=a%5E",                        [('one', 'a^')]),
            ("&",                               []),
            ("one=1&two&one=2",                 [('one', '1'), ('two', ''), ('one', '2')]),
            ("one=1&two=&one=2",                [('one', '1'), ('two', ''), ('one', '2')]),
            ("one two=1&one%two=2",             [('one two', '1'), ('one%two', '2')]),
            ("&".join([Query.SAFE_NAME_CHARS + "=" + Query.SAFE_VALUE_CHARS] * 5),
                [(Query.SAFE_NAME_CHARS, Query.SAFE_VALUE_CHARS)] * 5),
            ("&".join([urllib.quote(quotedNameCharsStr, Query.SAFE_NAME_CHARS) + "=" + \
                urllib.quote(quotedValueCharsStr, Query.SAFE_VALUE_CHARS)] * 5),
                    [(quotedNameCharsStr, quotedValueCharsStr)] * 5),
            ("&".join(map(str, [1, 2, 3, 4, 5, 4, 3, 2, 1])),
                [(num, '') for num in map(str, [1, 2, 3, 4, 5, 4, 3, 2, 1])]),
            ("onéě=unicodé",                     [("onéě", "unicodé")])]

        self.testMappings = [
            [('one', '1'), ('two', '2'), ('three', '2')],
            [('one one', '1'), ('two+two', '2')],
            [('one%5Eone', '1'), ('two two', '')]]

    def _initQurey(self):
        for init, mapping in self._queryInits():
            yield Query(init), mapping

    def _queryInits(self):
        result = []
        for string , mapping in self.testParseStrings:
            result.append((string, mapping))
            result.append((Query.parse(string), mapping))
            result.append((omdict(Query.parse(string)), mapping))
            result.append((dict(Query.parse(string)), dict(mapping).items()))
        for mapping in self.testMappings:
            result.append((mapping, mapping))
            result.append((omdict(mapping), mapping))
            result.append((dict(mapping), dict(mapping).items()))
        for init, mapping in result:
            yield init, mapping

    def _stringFromMapping(self, mapping, delimeter = '&'):
        def quote(name, value):
            return (http.urlQuotePlus(name, Query.SAFE_NAME_CHARS),
                http.urlQuotePlus(value, Query.SAFE_VALUE_CHARS))
        return delimeter.join(["=".join(quote(name, value)) for name, value in mapping])

    def test_parse(self):
        for string, mapping in self.testParseStrings:
            self.assertEquals(Query.parse(string), mapping)

    def test_init(self):
        for query, mapping in self._initQurey():
            self.assertEquals(query.params.allitems(), mapping)
            self.assertEquals(query.params, omdict(mapping))

    def test_initWrongType(self):
        self.assertRaises(TypeError, Query, object())

    def test_initMapingWithNoString(self):
        mappings = [[('one', '1'), ('two', '2'), ('three', object())],
                    [('one', '1'), ('two', '2'), (object(), '3')]]
        for i in mappings:
            self.assertRaises(TypeError, Query, i)

    def lest_load(self):
        for query, m in self._initQurey():
            self.assertEquals(query.params.allitems(), m)
            for init, mapping in self._queryInits():
                self.assertEquals(query.load(init), query)
                self.assertEquals(query.params.allitems(), mapping)

    def test_loadWrongType(self):
        for query, mapping in self._initQurey():
            self.assertRaises(TypeError, query.load, object())
            self.assertEquals(query.params.allitems(), mapping)

    def testLoadMappingWithNoString(self):
        mappings = [[('one', '1'), ('two', '2'), ('three', object())],
                    [('one', '1'), ('two', '2'), (object(), '3')]]
        for query, mapping in self._initQurey():
            for i in mappings:
                self.assertRaises(TypeError, query.load, i)
                self.assertEquals(query.params.allitems(), mapping)

    def test_paramsGetter(self):
        for query, mapping in self._initQurey():
            self.assertIsInstance(query.params, omdict)

    def test_paramsSetter(self):
        for query , m in self._initQurey():
            self.assertEquals(query.params.allitems(), m)
            for init, mapping in self._queryInits():
                query.params = init
                self.assertEquals(query.params.allitems(), mapping)

    def test_paramsSetterWrongType(self):
        for query, mapping in self._initQurey():
            self.assertRaises(TypeError, query.__setattr__, 'params', object())
            self.assertEquals(query.params.allitems(), mapping)

    def test_paramsSetterMappingWithNoString(self):
        mappings = [[('one', '1'), ('two', '2'), ('three', object())],
                    [('one', '1'), ('two', '2'), (object(), '3')]]
        for query, mapping in self._initQurey():
            for i in mappings:
                self.assertRaises(TypeError, query.__setattr__, 'params', i)
                self.assertEquals(query.params.allitems(), mapping)

    def test_delimeterGetter(self):
        self.assertEquals(Query("").delimeter, "&")
        self.assertEquals(Query("", delimeter = ";").delimeter, ";")

    def test_delimeterSetter(self):
        query = Query("")
        self.assertEquals(query.delimeter, "&")
        query.delimeter = "test"
        self.assertEquals(query.delimeter, "test")

    def test_delimeterSetterNoStringError(self):
        query = Query("")
        self.assertRaises(TypeError, query.__setattr__, 'delimeter', object())
        self.assertEquals(query.delimeter, "&")

    def test_add(self):
        for query, mapping in self._initQurey():
            for init, addMapping in self._queryInits():
                oldMapping = query.params.allitems()
                self.assertEquals(query.add(init), query)
                self.assertEquals(query.params.allitems(), oldMapping + addMapping)

    def test_addWrongTypeError(self):
        for query, mapping in self._initQurey():
            self.assertRaises(TypeError, query.add, object())
            self.assertEquals(query.params.allitems(), mapping)

    def test_addMappingWithNoStringError(self):
        mappings = [[('one', '1'), ('two', '2'), ('three', object())],
                    [('one', '1'), ('two', '2'), (object(), '3')]]
        for query, mapping in self._initQurey():
            for i in mappings:
                self.assertRaises(TypeError, query.add, i)
                self.assertEquals(query.params.allitems(), mapping)

    def test_clear(self):
        for query, mapping in self._initQurey():
            self.assertEquals(query.clear(), query)
            self.assertEquals([], query.params.allitems())

    def test_str(self):
        for query, mapping in self._initQurey():
            self.assertEquals(unicode(query), self._stringFromMapping(mapping))

    def test_repr(self):
        for query, mapping in self._initQurey():
            self.assertEquals(repr(query), "<%s ('%s')>" %
                (query.__class__.__name__, self._stringFromMapping(mapping)))

    def test_nonzero(self):
        for query, mapping in self._initQurey():
            if len(mapping) > 0:
                self.assertTrue(query)
            else:
                self.assertFalse(query)

    def test_eqTrue(self):
        for query, mapping in self._initQurey():
            self.assertTrue(query.__eq__(Query(mapping)))

    def test_eqFalse(self):
        for query, mapping in self._initQurey():
            query.params.add("inique", "unique")
            self.assertFalse(query.__eq__(Query(mapping)))

    def test_eqNotImplemented(self):
        for query, mapping in self._initQurey():
            self.assertEquals(NotImplemented, query.__eq__(object()))

    def test_neTrue(self):
        for query, mapping in self._initQurey():
            query.params.add("inique", "unique")
            self.assertTrue(query.__ne__(Query(mapping)))

    def test_neFalse(self):
        for query, mapping in self._initQurey():
            self.assertFalse(query.__ne__(Query(mapping)))

    def test_neNotImplemented(self):
        for query, mapping in self._initQurey():
            self.assertEquals(NotImplemented, query.__ne__(object()))

class TestUrl(unittest.TestCase):

    def setUp(self):
        pass

    def test_url1(self):
        u = Url("http://user:secret@example.com/index.html?key=value")
        self.assertEquals(u.scheme, "http")
        self.assertEquals(u.username, "user")
        self.assertEquals(u.password, "secret")
        self.assertEquals(u.userInfo, "user:secret")
        self.assertEquals(u.host, "example.com")
        self.assertEquals(u.port, 80)
        self.assertFalse(u.explicitPort)
        self.assertEquals(str(u.path), "/index.html")
        self.assertEquals(str(u.query), "key=value")

    def test_usernameAndPassword(self):
        urls = [
            ("http://user:secret@example.com/", "user", "secret"),
            ("http://user@example.com/", "user", None),
            ("http://:secret@example.com/", "", "secret"),
            ("http://example.com/", None, None)]
        for string, username, password in urls:
            u = Url(string)
            self.assertEquals(u.username, username)
            self.assertEquals(u.password, password)

    def test_userInfo(self):
        urls = [
            ("http://user:secret@example.com/", "user:secret"),
            ("http://user@example.com/", "user"),
            ("http://:secret@example.com/", ":secret"),
            ("http://example.com/", None)]
        for string, userInfo in urls:
            self.assertEquals(Url(string).userInfo, userInfo)

    def test_netloc(self):
        urls = [
                ("http://user:secret@example.com/index.html?key=value", "user:secret@example.com"),
                ("http://user:secret@example.com:80/index.html?key=value", "user:secret@example.com:80"),
                ("http://user@example.com/index.html?key=value", "user@example.com"),
                ("http://:secret@example.com/index.html?key=value", ":secret@example.com"),
                ("http://example.com/index.html?key=value", "example.com"),
                ("http://example.com:80/index.html?key=value", "example.com:80")]
        for string, netloc in urls:
            self.assertEquals(Url(string).netloc, netloc)

    def test_eq(self):
        urls = [
            ("http://example.com",          "http://example.com")]
        for init1, init2 in urls:
            self.assertEquals(Url(init1), Url(init2))

class _TestWebUrl(object):

    u = None

    def setUp(self):
        self.testInitSrings = [
                ("http:")]

    def tearDown(self):
        self.u = None

    def test_scheme(self):
        self.assertEquals("http", self.u.getScheme())

    def test_username(self):
        self.assertEquals("user", self.u.getUsername())

    def test_password(self):
        self.assertEquals("secret", self.u.getPassword())

    def test_location(self):
        self.assertEquals("www.google.com", self.u.getLocation())

    def test_isSecureFalse(self):
        self.assertFalse(self.u.isSecure())

    def test_isSecureTrue(self):
        self.u = url.WebUrl("https://user:secret@www.google.com/path/to/index.html?query1=one&query2=two#fragment")
        self.assertTrue(self.u.isSecure())

    def test_haveStandardPort80(self):
        self.assertTrue(self.u.haveStandardPort())

    def test_haveStandardPort443(self):
        self.u = url.WebUrl("https://user:secret@www.google.com/path/to/index.html?query1=one&query2=two#fragment")
        self.assertTrue(self.u.haveStandardPort())

    def test_getPort80(self):
        self.assertEquals(80, self.u.getPort())

    def test_getPort443(self):
        self.u = url.WebUrl("https://user:secret@www.google.com/path/to/index.html?query1=one&query2=two#fragment")
        self.assertEquals(443, self.u.getPort())

    def test_getPortExplicit(self):
        self.u = url.WebUrl("https://user:secret@www.google.com:8080/path/to/index.html?query1=one&query2=two#fragment")
        self.assertEquals(8080, self.u.getPort())

    def test_path(self):
        self.assertEquals("/path/to/index.html", self.u.getPath())

    def test_querySimple(self):
        self.assertEquals(2, len(self.u.getQueries()))
        self.assertEquals("query1", self.u.getQueries()[0][0])
        self.assertEquals("one", self.u.getQueries()[0][1])
        self.assertEquals("query2", self.u.getQueries()[1][0])
        self.assertEquals("two", self.u.getQueries()[1][1])

    def test_eqPath(self):
        self.assertEquals(
            url.WebUrl("http://www.example.com"),
            url.WebUrl("http://www.example.com/"))

    def test_eqCase1(self):
        self.assertEquals(
            url.WebUrl("http://www.exaMple.com/"),
            url.WebUrl("http://www.example.com/"))

    def test_eqCase2(self):
        self.assertEquals(
            url.WebUrl("http://www.EXAMPLE.COM/"),
            url.WebUrl("http://www.example.com/"))

    def test_eqCase3(self):
        self.assertEquals(
            url.WebUrl("HTTP://www.example.com/"),
            url.WebUrl("http://www.example.com/"))

    def test_eqPort80(self):
        self.assertEquals(
            url.WebUrl("http://www.example.com:80/"),
            url.WebUrl("http://www.example.com/"))

    def test_eqPort443(self):
        self.assertEquals(
            url.WebUrl("https://www.example.com:443/"),
            url.WebUrl("https://www.example.com/"))

    def test_eqEmptyQuery(self):
        self.assertEquals(
            url.WebUrl("http://www.example.com/?"),
            url.WebUrl("http://www.example.com/"))

    def test_wrongShemeError(self):
        self.assertRaises(AttributeError, url.WebUrl, "ftp://www.example.com/")

    def _complexQuery(self):
        self.assertEquals(3, len(self.u.getQueries()))
        self.assertEquals("one", self.u.getQueries()[0][0])
        self.assertEquals("1", self.u.getQueries()[0][1])
        self.assertEquals("two", self.u.getQueries()[1][0])
        self.assertEquals("", self.u.getQueries()[1][1])
        self.assertEquals("three", self.u.getQueries()[2][0])
        self.assertEquals("3", self.u.getQueries()[2][1])

    def test_complexQueryParse1(self):
        self.u = url.WebUrl("http://example.com/?one=1&two=&three=3")
        self._complexQuery()
        self.assertEquals("http://example.com/?one=1&two=&three=3", str(self.u))

    def test_complexQueryParse2(self):
        self.u = url.WebUrl("http://example.com/?one=1&two&three=3")
        self._complexQuery()
        self.assertEquals("http://example.com/?one=1&two=&three=3", str(self.u))

    def test_blankPassword(self):
        self.u = url.WebUrl("http://user@example.com/")
        self.assertEquals("user", self.u.getUsername())
        self.assertIsNone(self.u.getPassword())
        self.assertEquals("http://user@example.com/", str(self.u))

    def test_blankUsername(self):
        self.u = url.WebUrl("http://:pass@example.com/")
        self.assertEquals("pass", self.u.getPassword())
        self.assertIsNone(self.u.getUsername())
        self.assertEquals("http://:pass@example.com/", str(self.u))

    def test_fullCredentialsTrue(self):
        self.assertTrue(self.u.fullCredentials())

    def test_fullCredentialsFalse(self):
        self.u = url.WebUrl("http://user@example.com/")
        self.assertFalse(self.u.fullCredentials())

    def test_notEq(self):
        self.assertNotEquals(
            url.WebUrl("http://example.com/"),
            object())
