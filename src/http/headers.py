from __future__ import unicode_literals


class Header(object):
    """
    representaion of http header
    """

    __name = None
    __value = None

    def __init__(self, name, value):
        self.__name = self.__checkStringValue(name)
        self.__value = self.__checkStringValue(value)

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
        self.__checkStringValue(value)

    def __checkStringValue(self, value):
        if not isinstance(value, basestring):
            raise TypeError, "value must be string"
        return value

    def __unicode__(self):
        return self.name + ": " + unicode(self.value)

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __repr__(self):
        return b"<%s ('%s')>" % (self.__class__.__name__, str(self))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        else:
            return unicode(self) == unicode(other)

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        else:
            return not result

    # define factory methods

    @classmethod
    def cookie(cls, cookie):
        return cls("Cookie", cookie.cookieString())

    @classmethod
    def setCookie(self, cookie):
        return cls("Set-Cookie", cookie.setCookieString())
