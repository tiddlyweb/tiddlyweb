"""
WSGI Middleware that extracts ``CGI`` parameters from the
``QUERY_STRING`` and puts them in ``tiddlyweb.query`` in the
environ in the same structure that cgi.py uses (dictionary of lists).
If the current request is a ``POST`` of HTML form data, parse that too.
"""

# XXX not using tiddlyweb.fixups here because of ENCODED_QUERY
# presumably there is a way around that.
try:
    from urllib.parse import parse_qs
    ENCODED_QUERY = False
except ImportError:
    try:
        from urlparse import parse_qs
    except ImportError:
        from cgi import parse_qs
    ENCODED_QUERY = True

from httpexceptor import HTTP400

from tiddlyweb.filters import parse_for_filters
from tiddlyweb.web.util import read_request_body

try:
    unicode
except NameError:
    def unicode(input, encoding=None):
        return input


class Query(object):
    """
    Extract ``CGI`` parameter data from ``QUERY_STRING`` and POSTed form data.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        self.extract_query(environ)
        return self.application(environ, start_response)

    def extract_query(self, environ):
        """
        Read the ``QUERY_STRING`` and body (if a POSTed form) to extract
        query parameters. Put the results in ``tiddlyweb.query`` in
        environ. The query names and values are decoded from UTF-8 to
        unicode.
        """
        content_type = environ.get('CONTENT_TYPE', '')
        environ['tiddlyweb.query'] = {}
        if environ['REQUEST_METHOD'].upper() == 'POST' and \
                content_type.startswith('application/x-www-form-urlencoded'):
            try:
                try:
                    length = environ['CONTENT_LENGTH']
                    content = read_request_body(environ, length)
                    if not ENCODED_QUERY:
                        content = content.decode('UTF-8')
                except KeyError as exc:
                    raise HTTP400('Invalid post, unable to read content: %s'
                            % exc)
                posted_data = parse_qs(content, keep_blank_values=True)
                _update_tiddlyweb_query(environ, posted_data,
                        encoded=ENCODED_QUERY)
            except UnicodeDecodeError as exc:
                raise HTTP400(
                        'Invalid encoding in query data, utf-8 required: %s',
                        exc)
        filters, leftovers = parse_for_filters(
                environ.get('QUERY_STRING', ''), environ)
        query_data = parse_qs(leftovers, keep_blank_values=True)
        try:
            _update_tiddlyweb_query(environ, query_data, encoded=ENCODED_QUERY)
        except UnicodeDecodeError as exc:
            raise HTTP400(
                    'Invalid encoding in query string, utf-8 required: %s',
                    exc)
        environ['tiddlyweb.filters'] = filters


def _update_tiddlyweb_query(environ, data, encoded=True):
    if encoded:
        environ['tiddlyweb.query'].update(dict(
            [(unicode(key, 'UTF-8'), [unicode(value, 'UTF-8')
                for value in values]) for key, values in data.items()]))
    else:
        environ['tiddlyweb.query'].update(data)
