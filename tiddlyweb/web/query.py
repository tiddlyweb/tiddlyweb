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

from cgi import FieldStorage

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

        If there are file uploads in posted form data, the files are
        not put into ``tiddlyweb.query``. Instead the file handles are
        appended to ``tiddlyweb.input_files``.
        """
        content_type = environ.get('CONTENT_TYPE', '')
        environ['tiddlyweb.query'] = {}
        environ['tiddlyweb.input_files'] = []
        if _cgi_post(environ, content_type):
            _process_post(environ, content_type)
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
    """
    Update ``tiddlyweb.query`` with decoded form data.
    """
    if encoded:
        environ['tiddlyweb.query'].update(dict(
            [(unicode(key, 'UTF-8'), [unicode(value, 'UTF-8')
                for value in values]) for key, values in data.items()]))
    else:
        environ['tiddlyweb.query'].update(data)


def _cgi_post(environ, content_type):
    """
    Test if there is POST form data to handle.
    """
    return (environ['REQUEST_METHOD'].upper() == 'POST'
            and (
                content_type.startswith('application/x-www-form-urlencoded')
                or content_type.startswith('multipart/form-data')))


def _process_post(environ, content_type):
    """
    Process posted form data.
    """
    try:
        if content_type.startswith('application/x-www-form-urlencoded'):
            posted_data = _process_encodedform(environ)
        elif content_type.startswith('multipart/form-data'):
            posted_data = _process_multipartform(environ)
        _update_tiddlyweb_query(environ, posted_data, encoded=ENCODED_QUERY)
    except UnicodeDecodeError as exc:
        raise HTTP400(
                'Invalid encoding in query data, utf-8 required: %s',
                exc)


def _process_encodedform(environ):
    """
    Read ``application/x-www-form-urlencoded`` from the request
    body and parse for form data and return.
    """
    try:
        length = environ['CONTENT_LENGTH']
        content = read_request_body(environ, length)
        if not ENCODED_QUERY:
            content = content.decode('UTF-8')
    except KeyError as exc:
        raise HTTP400('Invalid post, unable to read content: %s' % exc)
    return parse_qs(content, keep_blank_values=True)


def _process_multipartform(environ):
    """
    Read ``multipart/form-data`` using ``FieldStorage``, return
    a dictionary of form data and set ``tiddlyweb.input_files``
    to a list of available files.
    """
    posted_data = {}
    try:
        field_storage = FieldStorage(fp=environ['wsgi.input'],
                environ=environ, keep_blank_values=True)
    except ValueError as exc:
        raise HTTP400('Invalid post, bad form: %s' % exc)
    for key in field_storage.keys():
        if (hasattr(field_storage[key], 'filename')
                and field_storage[key].filename):
            environ['tiddlyweb.input_files'].append(
                    field_storage[key])
        else:
            posted_data[key] = field_storage.getlist(key)
    return posted_data
