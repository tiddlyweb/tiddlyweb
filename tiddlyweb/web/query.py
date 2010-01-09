"""
WSGI Middleware that extracts CGI parameters
from the QUERY_STRING and puts them in
tiddlyweb.query in the same structure that
cgi.py users (dictionary of lists).
"""

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from tiddlyweb.filters import parse_for_filters


class Query(object):
    """
    We do this for "future expansion" and to
    remove some duplication throughout the
    code.

    Possible future expansion includes things like
    parameter filtering and what not.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        self.extract_query(environ)
        return self.application(environ, start_response)

    def extract_query(self, environ):
        content_type = environ.get('CONTENT_TYPE', '')
        environ['tiddlyweb.query'] = {}
        if environ['REQUEST_METHOD'].upper() == 'POST' and \
                content_type.startswith('application/x-www-form-urlencoded'):
            length = environ['CONTENT_LENGTH']
            content = environ['wsgi.input'].read(int(length))
            posted_data = parse_qs(content, keep_blank_values=True)
            _update_tiddlyweb_query(environ, posted_data)
        filters, leftovers = parse_for_filters(environ.get('QUERY_STRING', ''), environ)
        query_data = parse_qs(leftovers, keep_blank_values=True)
        _update_tiddlyweb_query(environ, query_data)
        environ['tiddlyweb.filters'] = filters


def _update_tiddlyweb_query(environ, data):
    environ['tiddlyweb.query'].update(dict(
        [(unicode(key, 'UTF-8'), [unicode(value, 'UTF-8') for value in values])
            for key, values in data.items()]))
