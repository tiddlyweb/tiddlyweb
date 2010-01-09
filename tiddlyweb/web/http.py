"""
A group of exception classes representating HTTP error
statuses, along with a WSGI middleware to turn the
exceptions into proper HTTP headers.

These exception need messages and a base class so
we don't need all the code in HTTPExceptor.
"""

import logging
import sys
import traceback


class HTTPException(Exception):
    """
    Base class of an HTTP exception, which in
    this context is a non 2xx response code.
    """
    status = ''

    def headers(self):
        """
        Set the content type of the response.
        """
        return [('Content-Type', 'text/plain; charset=UTF-8')]

    def output(self):
        """
        Output an error message.
        """
        if not hasattr(self, 'args'):
            self.args = '%s' % self
        if isinstance(self.args, unicode):
            self.args = self.args.encode('utf-8')
        return ['%s: %s' % (self.status, self.args)]


class HTTP302(HTTPException):
    status = '302 Found'

    def headers(self):
        return [('Location', '%s' % self)]

    def output(self):
        return ['']


class HTTP303(HTTP302):
    status = '303 See Other'


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
    """
    WSGI application that wraps internal WSGI
    applications and traps HTTPExceptionS and
    other exceptions. If the exceptions is an
    HTTPException we send a reasonable response
    to the browser. If the exception is some other
    form we do an HTTP 500 and send a traceback.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response, exc_info=None):
        try:
            return self.application(environ, start_response)
        except HTTPException, exc:
            start_response(exc.status, exc.headers(), exc_info)
            return exc.output()
        except:
            etype, value, traceb = sys.exc_info()
            exception_text = ''.join(traceback.format_exception(
                etype, value, traceb, None))
            print >> environ['wsgi.errors'], exception_text
            logging.warn(exception_text)
            start_response('500 server error',
                    [('Content-Type', 'text/plain')], sys.exc_info())
            return [exception_text]
