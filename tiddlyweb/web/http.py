"""
A group of exception classes representating HTTP error 
statuses, along with a WSGI middleware to turn the
exceptions into proper HTTP headers.

These exception need messages and a base class so 
we don't need all the code in HTTPExceptor.
"""
class HTTP415(Exception):
    pass

class HTTP403(Exception):
    pass

class HTTP404(Exception):
    pass

class HTTP409(Exception):
    pass

class HTTPExceptor(object):

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        try:
            return self.application(environ, start_response)
        except HTTP415, e:
            start_response("415 Unsupported", [('Content-Type', 'text/plain')])
            output = '415 Unsupported: %s' % e
            return [output]
        except HTTP409, e:
            start_response('409 Conflict', [('Content-Type', 'text/plain')])
            output = '409 Conflict: %s' % e
            return [output]
        except HTTP404, e:
            start_response("404 Not Found", [('Content-Type', 'text/plain')])
            output = '404 Not Found: %s' % e
            return [output]
        except HTTP403, e:
            start_response("403 Forbidden", [('Content-Type', 'text/plain')])
            output = '403 Forbidden: %s' % e
            return [output]
