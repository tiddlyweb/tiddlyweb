"""
A group of exception classes representating HTTP error
statuses, along with a WSGI middleware to turn the
exceptions into proper HTTP headers.

These exception need messages and a base class so
we don't need all the code in HTTPExceptor.

XXX: The Exceptor should log errors for each of
these exceptions as in the finall except clause.
"""

import sys
import traceback


class HTTPException(Exception):
    status = ''

    def headers(self):
        return [('Content-Type', 'text/plain; charset=UTF-8')]

    def output(self):
        if not hasattr(self, 'message'):
            self.message = '%s' % self
        if isinstance(self.message, unicode):
            self.message = self.message.encode('utf-8')
        return ['%s: %s' % (self.status, self.message)]


class HTTP302(HTTPException):
    status = '302 Found'

    def headers(self):
        return [('Location', '%s' % self)]

    def output(self):
        return ['']


class HTTP304(HTTPException):
    status = '304 Not Modified'

    def headers(self):
        return [('Etag', '%s' % self)]

    def output(self):
        return ['']


class HTTP400(HTTPException):
    status = '400 Bad Request'


class HTTP401(HTTPException):
    status = '401 Unauthorized'

    def headers(self):
        return [('WWW-Authenticate', '%s' % self)]

    def output(self):
        return ['']


class HTTP403(HTTPException):
    status = '403 Forbidden'


class HTTP404(HTTPException):
    status = '404 Not Found'


class HTTP409(HTTPException):
    status = '409 Conflict'


class HTTP412(HTTPException):
    status = '412 Precondition Failed'


class HTTP415(HTTPException):
    status = '415 Unsupported'


class HTTPExceptor(object):

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response, exc_info=None):
        try:
            return self.application(environ, start_response)
        except HTTPException, e:
            start_response(e.status, e.headers(), exc_info)
            return e.output()
        except:
            etype, value, tb = sys.exc_info()
            exception_text = ''.join(traceback.format_exception(etype, value, tb, None))
            print >> environ['wsgi.errors'], exception_text
            start_response('500 server error', [('Content-Type', 'text/plain')], sys.exc_info())
            return [exception_text]
