"""
A group of exception classes representing HTTP error statuses, along
with a WSGI middleware to turn the exceptions into proper HTTP headers.

Anywhere in the stack, if an HTTP response other than 2xx is required
just raise an HTTP<something> and this module will catch it and create
the correct response to send to the client.
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
            self.args = ('%s' % self, )
        output = []
        for arg in self.args:
            if isinstance(arg, unicode):
                arg = arg.encode('utf-8')
            output.append('%s' % arg)
        return ['%s: %s' % (self.status, ' '.join(output))]


class HTTP302(HTTPException):
    """302 Found"""

    status = __doc__

    def headers(self):
        """
        A 302 requires a location header.
        """
        return [('Location', '%s' % self)]

    def output(self):
        """
        A 302 _must_ have no output.
        """
        return ['']


class HTTP303(HTTP302):
    """303 See Other"""

    status = __doc__


class HTTP304(HTTPException):
    """304 Not Modified"""

    status = __doc__

    def headers(self):
        """
        Send an ETag with a 304.
        """
        return [('Etag', '%s' % self)]

    def output(self):
        """
        A 304 must not include a body.
        """
        return ['']


class HTTP400(HTTPException):
    """400 Bad Request"""

    status = __doc__


class HTTP401(HTTPException):
    """401 Unauthorized"""

    status = __doc__

    def headers(self):
        """
        A WWW-Authenticate header is expected with a 401.
        """
        return [('WWW-Authenticate', '%s' % self)]

    def output(self):
        """
        No body with a 401.
        """
        return ['']


class HTTP403(HTTPException):
    """403 Forbidden"""

    status = __doc__


class HTTP404(HTTPException):
    """404 Not Found"""

    status = __doc__


class HTTP409(HTTPException):
    """409 Conflict"""

    status = __doc__


class HTTP412(HTTPException):
    """412 Precondition Failed"""

    status = __doc__


class HTTP415(HTTPException):
    """415 Unsupported"""

    status = __doc__


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
