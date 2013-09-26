# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import tools
from http.utils import urlQuote, urlQuotePlus, urlUnquote, urlUnqoutePlus
import collections
import urlparse
import ipaddr
import re
import python.orderedmultidict1d



class Path(object):
    """
    Representation of URL path. Path can be created from iterable with strings
    or from one string
    """

    # define characters which don't have to be quoted
    SAFE_SEGMENT_CHARS = ":@-._~!$&'()*+,;="

    __segments = None

    def __init__(self, iterable):
        self.segments = self.__getSegmentList(iterable)

    @property
    def segments(self):
        return self.__segments

    @segments.setter
    def segments(self, iterable):
        self.__segments = self.__getSegmentList(iterable)

    def __getSegmentList(self, iterable):
        """
        return list of strings from iterable
        """
        l = []
        if isinstance(iterable, basestring):
            return self.__class__.parse(iterable)
        try:
            for segment in iterable:
                assert isinstance(segment, basestring)
                l.append(segment)
        except Exception:
            raise TypeError, "iterable must be iterable with strings"
        return l

    def load(self, iterable):
        """
        Load new path segments, replacing any existing ones.
        """
        self.segments = self.__getSegmentList(iterable)
        return self

    def add(self, iterable):
        """
        Add path segments to current ones.

        note:
            if you are adding list of segments, they will be interpreted as
            character, wich needs to be quoted

            path = Path.fromString(/path)
            path.add(["to", "some/resource"])
            str(path) == "/path/to/some%2Fresource"
        """
        self.__segments.extend(self.__getSegmentList(iterable))
        return self

    def clear(self):
        """
        clear any existing path segments
        """
        self.segments = []
        return self

    @classmethod
    def parse(cls, path):
        """
        parse path string into list of segments
        """
        toReturn = []
        split = path.split('/')
        for i in xrange(len(split)):
            if len(split[i]) > 0 or (not i < len(split) - 1 and len(toReturn) > 0):
                toReturn.append(
                    urlUnquote(
                        split[i]))
        return toReturn

    @classmethod
    def fromString(cls, path):
        """
        create new Path object from string
        """
        return cls(cls.parse(path))

    def __repr__(self):
        return "<%s ('%s')>" % (self.__class__.__name__, str(self))

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __unicode__(self):
        def quote(segment):
            return urlQuote(segment, self.SAFE_SEGMENT_CHARS)
        return '/' + '/'.join(map(quote, self.__segments))

    def __nonzero__(self):
        return len(self.__segments) > 0

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return other.segments == self.segments

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        else:
            return not result

class Query(object):
    """
    Representation of URL query
    """

    SAFE_NAME_CHARS   = "/?:@-._~!$'()*,"
    SAFE_VALUE_CHARS = "/?:@-._~!$'()*,="

    # query parameters
    __params = None
    __delimeter = None

    def __init__(self, mapping, delimeter = '&'):
        self.__delimeter = delimeter
        self.__params = self.__getOmdict(mapping)

    def load(self, mapping):
        """
        Load query replacing an existing one. Mapping is iterable with
        (name, value) tuples
        """
        self.params.load(self.__getOmdict(mapping))
        return self

    def __getOmdict(self, mapping):
        """
        create instance of various containers
        """
        m = []
        if isinstance(mapping, basestring):

            # omdict from string
            m = self.__class__.parse(mapping, delimeter = self.delimeter)
        elif isinstance(mapping, tools.omdict):

            # omdict
            m = mapping.allitems()
        elif isinstance(mapping, dict):

            # idct
            m = mapping.items()
        else:

            # iterable
            try:
                for name, value in mapping:
                    assert isinstance(name, basestring) and isinstance(value, basestring)
                    m.append((name, value))
            except Exception:
                raise TypeError
        return python.orderedmultidict1d.omdict1D(m)

    @property
    def params(self):
        """
        return instance of modified omdict - omdict1D. This type can be only
        one dimensional. Thats mean, if you will attemt to add an list into it
        will be expanded into sigle elements

        example:
            omd1d = query.params
            omd1d['key'] = [1, 2, 3]
            omd1d.getallitems() == [('key', 1), ('key', 2), ('key', 3)]
        """
        return self.__params

    @params.setter
    def params(self, params):
        """
        Set params. Params must  be type of omdict
        """
        self.__params = self.__getOmdict(params)

    @property
    def delimeter(self):
        return self.__delimeter

    @delimeter.setter
    def delimeter(self, delimeter):
        if not isinstance(delimeter, basestring):
            raise TypeError, "delimeter must be string"
        self.__delimeter = delimeter

    def add(self, mapping):
        """
        Add query to an existing query. query can either be iterable of
        (name, value) tuples or query string
        """
        self.params.load(self.params.allitems() + self.__getOmdict(mapping).allitems())
        return self

    def clear(self):
        """
        clear any existing queries
        """
        self.params.clear()
        return self

    def __repr__(self):
        return "<%s ('%s')>" % (self.__class__.__name__, str(self))

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __unicode__(self):
        def quote(name, value):
            return (urlQuotePlus(name, self.__class__.SAFE_NAME_CHARS),
                urlQuotePlus(value, self.__class__.SAFE_VALUE_CHARS))
        items = []
        for name, value in self.params.allitems():
            items.append("=".join(quote(name, value)))
        return self.delimeter.join(items)

    def __nonzero__(self):
        return len(self.params) > 0

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.params == other.params
        else:
            return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        else:
            return not result

    @classmethod
    def parse(cls, query, delimeter = '&'):
        """
        parse query string and return list of (name, value) tuples
        """
        if not isinstance(query, basestring):
            raise TypeError, "query must be string"
        if not isinstance(delimeter, basestring):
            raise TypeError, "delimeter must be string"
        return urlparse.parse_qsl(query, keep_blank_values = True)

    @classmethod
    def fromString(cls, query, delimeter = '&'):
        return cls(cls.parse(query, delimeter))

class Fragment(object):
    """
    Representation of URL fragment
    """

    __fragment = None

    def __init__(self, fragment):
        self.__fragment = self.__checkFragment(fragment)

    def load(self, fragment):
        """
        Load fragment replacing the original one. Fragment must be type of string
        """
        self.__fragment = self.__checkFragment(fragment)

    def add(self, fragment):
        """
        Add fragment to an existing fragment.
        """
        self.__fragment += self.__checkFragment(fragment)

    def clear(self):
        """
        remove fragment
        """
        self.__fragment = ""

    def __checkFragment(self, fragment):
        if not isinstance(fragment, basestring):
            raise TypeError, "fragment must be string"
        return fragment

    @classmethod
    def fromString(cls, fragment):
        return cls(fragment)

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __unicode__(self):
        return self.__fragment

    def __repr__(self):
        return "<%s ('%s')>" % (self.__class__.__name__, str(self))

    def __nonzero__(self):
        return len(self.__fragment) > 0

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return str(self) == str(other)

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        else:
            return not result

class Url(object):
    """
    object representing web url
    """

    __schemes = {
        "http"          : 80,
        "https"         : 443}

    # define url fields
    __scheme = None
    __username = None
    __password = None
    __host = None
    __port = None
    __path = None
    __query = None
    __fragment = None

    # mark, if url has explicitly specified port
    # Url('http://example.com/').explicitPort == False
    # Url('http://example.com:80/').explicitPort == True
    __explicitPort = None

    def __init__(self, url):
        if isinstance(url, _UrlPackage):
            pass
        elif isinstance(url, basestring):
            self.__initFromString(url)
        else:
            raise TypeError, "url must be string"

    def __initFromString(self, url):
        parse = urlparse.urlsplit(url)
        if not self.__allInformation(parse):
            raise ValueError, "provided url seems not to be absolute: %s" % (url,)
        self.__scheme = parse.scheme
        self.__username = parse.username
        self.__password = parse.password
        self.__host = parse.hostname
        self.__port = parse.port
        self.__path = Path(parse.path)
        self.__query = Query(parse.query)
        self.__fragment = Fragment(parse.fragment)
        self.__explicitPort = (parse.port is not None)

    def __allInformation(self, parse):
        """
        returns True uf parse contain all requred informations to construst
        absolule url
        """
        return parse.scheme != "" and parse.netloc != ""

    # define properties

    @property
    def scheme(self):
        """
        scheme used by url
        """
        return self.__scheme

    @scheme.setter
    def scheme(self, scheme):
        self.__scheme = self.__stringAttribute(scheme)

    @property
    def username(self):
        """
        username specified in url. None if username not set. Can be deleted.
        """
        return self.__username

    @username.setter
    def username(self, username):
        self.__username = self.__stringAttribute(username) if username is not None else None

    @username.deleter
    def username(self):
        self.__username = None

    @property
    def password(self):
        """
        Password specified in url. None if password not set. Can be deleted.
        """
        return self.__password

    @password.setter
    def password(self, password):
        self.__password = self.__stringAttribute(password) if password is not None else None

    @password.deleter
    def password(self):
        self.__password = None

    @property
    def userInfo(self):
        """
        Retun user credentials, if username or password is set. If their are
        both None, then userInfo is None

        return table:
            username        password        userInfo
            -----------------------------------------------------
            'user'          'pass'          'user:pass'
            'user'          None            'user'
            ''              'pass'          ':pass'
            None            None            None
        """
        if self.username is None and self.password is None:
            return None
        elif self.username is not None and self.password is None:
            return self.username
        else:
            return self.username + ":" + self.password

    @property
    def host(self):
        """
        Host in url. Can be hostname of IP address. type of string
        """
        return self.__host

    @host.setter
    def host(self, host):
        self.__host = self.__stringAttribute(host)

    @property
    def port(self):
        if self.__port is None and self.scheme in self.__schemes:
            return self.__schemes[self.scheme]
        else:
            return self.__port

    @port.setter
    def port(self, port):
        self.__port = self.__intAttribute(port) if port is not None else None

    @port.deleter
    def port(self):
        self.__port = None

    @property
    def netloc(self):
        """
        netloc is combination of username, password, host and port
        if port ist't explicitly specified, it is also omnited in netloc
        """
        userInfo = (self.userInfo + "@") if self.userInfo is not None else ''
        port = (":" + str(self.port)) if self.explicitPort else ''
        return userInfo + self.host + port

    @property
    def path(self):
        """
        return object representing url path
        """
        return self.__path

    @path.setter
    def path(self, iterable):
        self.__path = Path(iterable)

    @path.deleter
    def path(self):
        self.path.clear()

    @property
    def query(self):
        """
        return object representing url query
        """
        return self.__query

    @query.setter
    def query(self, mapping):
        self.__query = Query(mapping)

    @query.deleter
    def query(self):
        self.query.clear()

    @property
    def fragment(self):
        return self.__fragment

    @fragment.setter
    def fragment(self, fragment):
        self.__fragment = Fragment(fragment)

    @fragment.deleter
    def fragment(self):
        self.fragment.clear()

    @property
    def explicitPort(self):
        """
        True if port is specified in url string representaton. You can set
        this value to False. If url has non-standard port defined,
        AttributeError is raised while attempting to hide port number
        """
        return self.__explicitPort

    @explicitPort.setter
    def explicitPort(self, explicitPort):
        if not self.hasStandardPort():
            raise AttributeError, "port is not standard, can't be changed"
        self.__explicitPort = self.__boolAttribute(explicitPort)

    def hasStandardPort(self):
        """
        True if url scheme is known scheme and associated port number match,
        of if scheme is unknown scheme (possibly standard port, but Url class
        isn't aware). False otherwise
        """
        if not self.scheme in self.__schemes:
            return True
        else:
            return self.port == self.__schemes[self.scheme]

    def __stringAttribute(self, attribute):
        """
        check if attribute is type of string
        """
        if not isinstance(attribute, basestring):
            raise TypeError, "expected string, not %s" % (type(attribute).__name__,)
        return attribute

    def __intAttribute(self, attribute):
        """
        check if attribute is type of int
        """
        if not isinstance(attribute, (int, long)):
            raise TypeError, "expected integer, not %s" % (type(attribure).__name__,)
        return attribute

    def __boolAttribute(self, attribute):
        """
        check if attribute is type of bool
        """
        if not isinstance(attribute, bool):
            raise TypeError, "expected boolean, not %s" % (type(attribute).__name__,)

    def __eq__(self, other):
        """
        Url comparison

        examples:
            Url("http://example.com/") == Url("http://example.com:80/")
            Url("http://example.com/") == Url("http://example.com/?")
            Url("http://example.com/") == Url("http://example.com")
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__compareUrls(other)

    def __compareUrls(self, other):
        return self.scheme == other.scheme and \
                self.username == other.username and \
                self.password == other.password and \
                self.host == other.host and \
                self.port == other.port and \
                self.path == other.path and \
                self.query == other.query and \
                self.fragment == other.fragment

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        else:
            return not result

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __unicode__(self):
        query = ("?" + unicode(self.query)) if self.query else ''
        fragment = ("#" + unicode(self.fragment)) if self.fragment else ''
        return self.scheme + "://" + self.netloc + unicode(self.path) + query + fragment

    def __repr__(self):
        return "<%s ('%s')>" % (self.__class__.__name__, str(self))

    @classmethod
    def join(cls, url, urlStr):
        """
        create new url from url object and string
        useful method for creating absolute urls from relative strings

        exapmple:
            u1 = Url("http://example.com/index.html")
            u2 = Url.join(u1, "/path/to/resource")
            str(u2) == "http://example.com/path/to/resource"
        """
        if not isinstance(url, cls) or not isinstance(urlStr, basestring):
            raise TypeError, "Url and string expected, not %s and %s" % \
                (type(url).__name__, type(urlStr).__name__)
        return cls(urlparse.urljoin(str(url), urlStr))

    @classmethod
    def buildUrl(cls):
        """
        build new url from parameters

        example:
            u = Url.buildUrl(
                "http",
                "example.com",
                path = ["path", "to", "resource"],
                query = [("one", 1), ("two", 2), ("one", 3)],
                fragment = "frag")
        """

    @classmethod
    def fromString(cls, rawString):
        """
        retin marity with orher url componenets
        """

class _UrlPackage(object):
    """
    Package for creating url without parsing. This method is used only by Url
    factory methods
    """
