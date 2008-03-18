
import os
import selector
from tiddlyweb.web.negotiate import Negotiate
from tiddlyweb.web.http import HTTPExceptor
from tiddlyweb.store import Store

def load_app(map, wrappers=[]):
    app = selector.Selector(mapfile=map)
    if wrappers:
        for wrapper in wrappers:
            app = wrapper(app)
    return app

def start_simple(filename, port):
    os.environ = {}
    from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
    httpd = WSGIServer(('', port), WSGIRequestHandler)
    httpd.set_app(default_app(filename))
    print "Serving HTTP on %s port %s ..." % httpd.socket.getsockname()
    httpd.serve_forever()

def default_app(filename):
    return load_app(filename, [StoreSet, Negotiate, HTTPExceptor, EncodeUTF8])
    #return load_app(filename, [StoreSet, Negotiate])

class StoreSet(object):

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        db = Store('text')
        environ['tiddlyweb.store'] = db
        return self.application(environ, start_response)

class EncodeUTF8(object):
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        return [x.encode('utf-8') for x in self.application(environ, start_response)]
