
import os
import selector
from tiddlyweb.web import negotiate
from tiddlyweb.store import Store

def load_app(map, wrappers=[]):
    app = selector.Selector(mapfile=map)
    if wrappers:
        def new_func(environ, start_response):
            for wrapper in wrappers:
                wrapper(environ, start_response)
            return app(environ, start_response)
        return new_func
    return app

def start_simple(filename, port):
    os.environ = {}
    from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
    httpd = WSGIServer(('', port), WSGIRequestHandler)
    httpd.set_app(default_app(filename))
    print "Serving HTTP on %s port %s ..." % httpd.socket.getsockname()
    httpd.serve_forever()

def default_app(filename):
    return load_app(filename, [negotiate.type, store])

def store(environ, start_response):
    """
    Stick a refernce to the canonical store
    in the environment. This allows us to
    maintain some config right here. Later
    this will be -actual- config.
    """
    db = Store('text')
    environ['tiddlyweb.store'] = db

