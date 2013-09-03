"""
http realated utilities
"""

from __future__ import unicode_literals
from urllib import unquote, unquote_plus
import string


alwaysSafe = string.ascii_letters.decode("utf-8") + \
    string.digits.decode("utf-8") + \
    "_.-"

def urlQuote(urlString, safeChars = "/"):
    if not isinstance(urlString, basestring) or \
            not isinstance(safeChars, basestring):
        raise TypeError, "both arguments must be strings"
    if not urlString:
        return urlString
    safe = alwaysSafe + safeChars
    charList = list(urlString)
    for i in xrange(len(charList)):
        if not charList[i] in safe:
            replace = ''
            for j in charList[i].encode("utf-8"):
                replace += "%%%02X" % ord(j)
            charList[i] = replace
    return "".join(charList)

def urlQuotePlus(urlString, safeChars = "/"):
    u = urlQuote(urlString, safeChars + ' ')
    return u.replace(' ', '+')

def urlUnquote(urlString):
    return unquote(urlString.encode("utf-8")).decode("utf-8")

def urlUnqoutePlus(urlString):
    return unquote_plus(urlString.encode("utf-8")).decode("utf-8")
