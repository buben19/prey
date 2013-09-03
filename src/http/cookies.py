from __future__ import unicode_literals
import datetime
import re
from ..url import Path



_coookieSeparatorPattern = re.compile(
    r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
_nameValueSeparatorPattern = re.compile(
    r'''(?P<name>[^=]+)(?:=(?:"){0,1}(?P<value>[^"]+)(?:"){0,1})?''')
_alfanumericCharsPattern = re.compile('[^\w ]+')
_singleSpacePatter = re.compile('[\s]{2,}')

class Cookie(object):
    """
    HTTP cookie
    """

    __name = None
    __value = None
    __expires = None
    __maxAge = None
    __domain = None
    __path = None
    __secure = None
    __httpOnly = None

    def __init__(self, cookieString):
        if isinstance(cookieString, _CookiePackage):
            self.__initFromPackage(cookieString)
        elif isinstance(cookieString, basestring):
            self.__initFromString(cookieString)
        else:
            raise TypeError, "cookie must be initialized from string"

    def __initFromString(self, cookieString):
        match = _coookieSeparatorPattern.findall(cookieString)
        package = _CookiePackage()
        for i in match:
            name, value = _nameValueSeparatorPattern.search(i).groups()
            name = name.strip()
            if value is not None:
                value = value.strip()
            if not package.nameAndValueSet():
                package.name = name
                package.value = value
            else:
                name = name.lower()
                if name in ['expires']:
                    package.expires = value
                elif name in ["maxage", "max-age"]:
                    package.maxAge = value
                elif name in ["domain"]:
                    package.domain = value
                elif name in ["path"]:
                    package.path = value
                elif name in ["secure"]:
                    package.secure = True
                elif name in ["httponly", "http-only"]:
                    package.httpOnly = True
        self.__initFromPackage(package)

    def __initFromPackage(self, cookiePackage):
        self.name       = cookiePackage.name
        self.value      = cookiePackage.value
        self.expires    = cookiePackage.expires
        self.maxAge     = cookiePackage.maxAge
        self.domain     = cookiePackage.domain
        self.path       = cookiePackage.path
        self.secure     = cookiePackage.secure
        self.httpOnly   = cookiePackage.httpOnly

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = self.__checkStringValue(name)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = self.__checkStringValue(value)

    @property
    def expires(self):
        return self.__expires

    @expires.setter
    def expires(self, expires):
        self.__expires = self.__getExpires(expires) if expires is not None else None

    @expires.deleter
    def expires(self):
        self.__expires = None

    @property
    def domain(self):
        return self.__domain

    @domain.setter
    def domain(self, domain):
        self.__domain = self.__checkStringValue(domain) if domain is not None else None

    @domain.deleter
    def domain(self):
        self.__domain = None

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path):
        self.__path = self.__getPath(path) if path is not None else None

    @path.deleter
    def path(self):
        self.__path = None

    @property
    def maxAge(self):
        return self.__maxAge

    @maxAge.setter
    def maxAge(self, maxAge):
        self.__maxAge = self.__getIntValue(maxAge) if maxAge is not None else None

    @maxAge.deleter
    def maxAge(self):
        self.__maxAge = None

    @property
    def httpOnly(self):
        return self.__httpOnly

    @httpOnly.setter
    def httpOnly(self, httpOnly):
        self.__httpOnly = self.__checkBooleanValue(httpOnly) if httpOnly is not None else None

    @httpOnly.deleter
    def httpOnly(self):
        self.__httpOnly = None

    @property
    def secure(self):
        return self.__secure

    @secure.setter
    def secure(self, secure):
        self.__secure = self.__checkBooleanValue(secure) if secure is not None else None

    @secure.deleter
    def secure(self):
        self.__secure = None

    def __checkStringValue(self, value):
        if not isinstance(value, basestring):
            raise TypeError, "value must be string"
        return value

    def __checkBooleanValue(self, value):
        if not isinstance(value, bool):
            raise TypeError, "value must be boolean"
        return value

    def __getExpires(self, expires):
        if isinstance(expires, datetime.datetime):
            return expires
        elif isinstance(expires, basestring):
            return self.__parseExpiresString(expires)
        else:
            raise TypeError, "expires must be datetime instance or string"

    def __parseExpiresString(self, expiresString):
        if expiresString.endswith("GMT"):
            expiresString = expiresString.replace("GMT", "")
        expiresString = _alfanumericCharsPattern.sub(' ', expiresString)
        expiresString = _singleSpacePatter.sub(' ', expiresString)
        expiresString = expiresString.strip()
        return datetime.datetime.strptime(expiresString, "%a %d %b %Y %H %M %S")

    def __getIntValue(self, value):
        if isinstance(value, (int, long)):
            return value
        elif isinstance(value, basestring):
            return int(value)
        else:
            raise TypeError, "value must be integer or string"

    def __getPath(self, path):
        if isinstance(path, Path):
            return path
        elif isinstance(path, basestring):
            return Path(path)
        else:
            raise TypeError, "path must be instance of path or string"

    @classmethod
    def fromString(cls, rawString):
        return cls(rawString)

    @classmethod
    def buildCookie(cls, name, value, expires = None, maxAge = None,
            domain = None, path = None, secure = False, httpOnly = False):
        """
        build cookie from parameters
        """
        return cls(_CookiePackage(
            name        = name,
            value       = value,
            expires     = expires,
            maxAge      = maxAge,
            domain      = domain,
            path        = path,
            secure      = secure,
            httpOnly    = httpOnly))

    def cookieString(self):
        """
        get cookie string representation which is send by client to the server
        (only name=value, no other attributes)
        """
        if ' ' in self.value or ';' in self.value:
            value = '"' + self.value + '"'
        else:
            value = self.value
        return "%s=%s" % (self.name, value)

    def setCookieString(self):
        """
        get cookie string representation whis is send by server to the client
        if Set-Cookie header
        """
        return unicode(self)

    def __unicode__(self):
        return self.cookieString() + \
            self.__createseAttributeString(self.expiresString()) + \
            self.__createseAttributeString(self.maxAgeString()) + \
            self.__createseAttributeString(self.domainString()) + \
            self.__createseAttributeString(self.pathString()) + \
            self.__createseAttributeString(self.secureString()) + \
            self.__createseAttributeString(self.httpOnlyString())

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __repr__(self):
        return b"<%s ('%s')>" % (self.__class__.__name__, str(self))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        else:
            unicode(self) == unicode(other)

    def __ne__(self):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        else:
            return not result

    def __separateAttribute(self, attributeString):
        return "; " + attributeString

    def expiresString(self):
        if self.expires is not None:
            return "Expires=%s GMT" % (self.expires.strftime("%a, %d %b %Y %H:%M:%S"))
        else:
            return None

    def domainString(self):
        if self.domain is not None:
            return "Domain=%s" % (self.domain,)
        else:
            return None

    def maxAgeString(self):
        if self.maxAge is not None:
            return "Max-Age=%d" % (self.maxAge,)
        else:
            return None

    def pathString(self):
        if self.path is not None:
            return "Path=%s" % (unicode(self.path),)
        else:
            return None

    def secureString(self):
        if self.secure:
            return "Secure"
        else:
            return None

    def httpOnlyString(self):
        if self.httpOnly:
            return "Httponly"
        else:
            return None

    def __createseAttributeString(self, attributeString):
        if attributeString is None:
            return ''
        else:
            return self.__separateAttribute(attributeString)

class _CookiePackage(object):

    name = None
    value = None
    expires = None
    maxAge = None
    domain = None
    path = None
    secure = None
    httpOnly = None

    def __init__(self, name = None, value = None, expires = None, maxAge = None,
            domain = None, path = None, secure = None, httpOnly = None):
        self.name       = name
        self.value      = value
        self.expires    = expires
        self.maxAge     = maxAge
        self.domain     = domain
        self.path       = path
        self.secure     = secure
        self.httpOnly   = httpOnly

    def nameAndValueSet(self):
        return self.name is not None and self.value is not None
