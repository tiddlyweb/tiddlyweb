"""
WSGI Middleware that extracts CGI parameters
from the QUERY_STRING and puts them in 
tiddlyweb.query in the same structure that
cgi.py users (dictionary of lists).

We do this for "future expansion" and to 
remove some duplication throughout the 
code.

Possible future expansion includes things like
parameter filtering and what not.
"""

import cgi

class Query(object):

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response, exc_info=None):
        self.extract_query(environ)
        return self.application(environ, start_response)

    def extract_query(self, environ):
        environ['tiddlyweb.query'] = cgi.parse_qs(environ.get('QUERY_STRING', ''))
