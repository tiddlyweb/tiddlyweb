
class HTTP415(Exception):
    pass

class HTTP404(Exception):
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
        except HTTP404, e:
            start_response("404 Not Found", [('Content-Type', 'text/plain')])
            output = '404 Not Found: %s' % e
            return [output]
