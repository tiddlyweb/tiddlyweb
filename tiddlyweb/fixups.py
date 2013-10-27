"""
Fixups used in various places to manage simultaneous support
for Python 2.7 and 3.
"""

try:
    unicode = unicode
except NameError:
    def unicode(input, encoding=None):
        return str(input)


try:
    basestring = basestring
    bytes = str
except NameError:
    basestring = str
    bytes = bytes


try:
    from Cookie import SimpleCookie, CookieError
except ImportError:
    from http.cookies import SimpleCookie, CookieError


try:
    from urllib import quote, unquote as unquote2

    def unquote(name):
        return unquote2(name.encode('utf-8')).decode('utf-8')
except ImportError:
    from urllib.parse import quote, unquote


try:
    from urllib.parse import parse_qs
except ImportError:
    try:
        from urlparse import parse_qs
    except ImportError:
        from cgi import parse_qs
