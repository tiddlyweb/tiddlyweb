
import os
import selector
from tiddlyweb.web import negotiate

def load_app(map, wrappers=[]):
    app = selector.Selector(mapfile=map)
    if wrappers:
        wrapper = wrappers[0]
        def new_func(environ, start_response):
            wrapper(environ, start_response)
            return app(environ, start_response)
        return new_func
    return app

def start_simple(filename, port):
    os.environ = {}
    from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
    httpd = WSGIServer(('', port), WSGIRequestHandler)
    httpd.set_app(load_app(filename, [negotiate.type]))
    print "Serving HTTP on %s port %s ..." % httpd.socket.getsockname()
    httpd.serve_forever()

