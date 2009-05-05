"""
WSGI Middleware that extracts CGI parameters
from the QUERY_STRING and puts them in
tiddlyweb.query in the same structure that
cgi.py users (dictionary of lists).
"""

import cgi

def select_parse(command):
    return 'select ' + command


def sort_parse(command):
    return 'sort ' + command


def limit_parse(command):
    return 'limit ' + command


FILTER_PARSERS = {
        'select': select_parse,
        'sort':   sort_parse,
        'limit':  limit_parse,
        }


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
            posted_data = cgi.parse_qs(content)
            environ['tiddlyweb.query'].update(posted_data)
        parse_for_filters(environ)


def parse_for_filters(environ):
    query_string = environ.get('QUERY_STRING', '')
    if ';' in query_string:
        strings = query_string.split(';')
    else:
        strings = query_string.split('&')

    filters = []
    leftovers = [] 
    for string in strings:
        query = cgi.parse_qs(string)
        try:
            key, value = query.items()[0]
            func = FILTER_PARSERS[key](value[0])
            filters.append(func)
        except(KeyError, IndexError):
            leftovers.append(string)

    leftovers = ';'.join(leftovers)
    environ['tiddlyweb.query'].update(cgi.parse_qs(leftovers))
    environ['tiddlyweb.filters'] = filters
