"""
WSGI Middleware that extracts CGI parameters from the QUERY_STRING and
puts them in tiddlyweb.query in the same structure that cgi.py users
(dictionary of lists). If the current request is a POST of form data,
parse that stuff too.
"""

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from tiddlyweb.filters import parse_for_filters
from tiddlyweb.web.http import HTTP400


class Query(object):
    """
    Extract CGI parameter data from QUERY_STRING and POSTed form data.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        self.extract_query(environ)
        return self.application(environ, start_response)

    def extract_query(self, environ):
        """
        Read the QUERY_STRING and body (if a POSTed form) to extract
        query paremeters. Put the results in tiddlyweb.query.
        """
        content_type = environ.get('CONTENT_TYPE', '')
        environ['tiddlyweb.query'] = {}
        if environ['REQUEST_METHOD'].upper() == 'POST' and \
                content_type.startswith('application/x-www-form-urlencoded'):
            try:
                length = environ['CONTENT_LENGTH']
                content = environ['wsgi.input'].read(int(length))
            except KeyError, exc:
                raise HTTP400('Invalid post, unable to read content: %s'
                        % exc)
            posted_data = parse_qs(content, keep_blank_values=True)
            try:
                _update_tiddlyweb_query(environ, posted_data)
            except UnicodeDecodeError, exc:
                raise HTTP400(
                        'Invalid encoding in query string, utf-8 required: %s',
                        exc)
        filters, leftovers = parse_for_filters(
                environ.get('QUERY_STRING', ''), environ)
        query_data = parse_qs(leftovers, keep_blank_values=True)
        try:
            _update_tiddlyweb_query(environ, query_data)
        except UnicodeDecodeError, exc:
            raise HTTP400(
                    'Invalid encoding in query string, utf-8 required: %s',
                    exc)
        environ['tiddlyweb.filters'] = filters


def _update_tiddlyweb_query(environ, data):
    environ['tiddlyweb.query'].update(dict(
        [(unicode(key, 'UTF-8'), [unicode(value, 'UTF-8') for value in values])
            for key, values in data.items()]))
